"""Three small security checks for a local crAPI learning lab."""

import argparse
import json
import os
from getpass import getpass
from pathlib import Path
from urllib.parse import urlsplit

import requests

LOGIN_PATH = "/identity/api/auth/login"
DASHBOARD_PATH = "/identity/api/v2/user/dashboard"
VEHICLES_PATH = "/identity/api/v2/vehicle/vehicles"
TIMEOUT = 10


def send_request(method, base_url, endpoint, token=None, data=None):
    """Use the same timeout and authorization format for every request."""
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    # A redirect to a login page should not look like successful API access.
    return requests.request(
        method, base_url + endpoint, headers=headers, json=data,
        timeout=TIMEOUT, allow_redirects=False,
    )


def read_json(response):
    """An HTML error page or empty response is not valid API evidence."""
    try:
        return response.json()
    except ValueError:
        return None


def make_result(check, endpoint, outcome, status_code, details):
    return {
        "check": check,
        "endpoint": endpoint,
        "outcome": outcome,
        "status_code": status_code,
        "details": details,
    }


def login(base_url, email, password):
    response = send_request(
        "POST", base_url, LOGIN_PATH,
        data={"email": email, "password": password},
    )
    data = read_json(response)
    if response.status_code != 200 or not isinstance(data, dict):
        raise ValueError(f"Login failed (HTTP {response.status_code}). Check the account and target URL.")
    token = data.get("token")
    if not isinstance(token, str) or not token.strip():
        raise ValueError("Login response did not contain a usable token.")
    return token


def broken_auth(base_url, token):
    """Compare a working authenticated dashboard with an anonymous request."""
    baseline = send_request("GET", base_url, DASHBOARD_PATH, token)
    dashboard = read_json(baseline)
    if (baseline.status_code != 200 or not isinstance(dashboard, dict)
            or dashboard.get("id") is None or not dashboard.get("email")):
        return make_result("Broken Authentication", DASHBOARD_PATH, "inconclusive",
                           baseline.status_code, "Could not read the authenticated dashboard.")

    response = send_request("GET", base_url, DASHBOARD_PATH)
    data = read_json(response)
    outcome = "inconclusive"
    details = "Unexpected response; this does not prove that authentication is secure."
    if response.status_code in (401, 403):
        outcome = "passed"
        details = "The API rejected this request without a token."
    elif (response.status_code == 200 and isinstance(data, dict)
          and data.get("id") is not None and data.get("email")):
        outcome = "finding"
        details = "The API returned user dashboard fields without a token. Review this exposure."
    return make_result("Broken Authentication", DASHBOARD_PATH, outcome,
                       response.status_code, details)


def bola(base_url, visitor_token, owner_token):
    """Try the owner's first vehicle using a different account's token."""
    # Verify different accounts using API identities, not just typed email addresses.
    visitor_response = send_request("GET", base_url, DASHBOARD_PATH, visitor_token)
    owner_response = send_request("GET", base_url, DASHBOARD_PATH, owner_token)
    visitor = read_json(visitor_response)
    owner = read_json(owner_response)
    if (visitor_response.status_code != 200 or owner_response.status_code != 200
            or not isinstance(visitor, dict) or not isinstance(owner, dict)
            or visitor.get("id") is None or owner.get("id") is None
            or visitor["id"] == owner["id"]):
        return make_result("BOLA", DASHBOARD_PATH, "inconclusive", None,
                           "Could not verify two different user identities.")

    response = send_request("GET", base_url, VEHICLES_PATH, owner_token)
    vehicles = read_json(response)
    if (response.status_code != 200 or not isinstance(vehicles, list) or not vehicles
            or not isinstance(vehicles[0], dict) or not vehicles[0].get("uuid")):
        return make_result("BOLA", VEHICLES_PATH, "inconclusive", response.status_code,
                           "Could not find the owner's vehicle. Add a vehicle to that account in crAPI.")

    vehicle_id = str(vehicles[0]["uuid"])
    endpoint = "/identity/api/v2/vehicle/" + vehicle_id + "/location"
    baseline = send_request("GET", base_url, endpoint, owner_token)
    owner_data = read_json(baseline)
    if (baseline.status_code != 200 or not isinstance(owner_data, dict)
            or owner_data.get("carId") != vehicle_id
            or not isinstance(owner_data.get("vehicleLocation"), dict)
            or not owner_data["vehicleLocation"]):
        return make_result("BOLA", endpoint, "inconclusive", baseline.status_code,
                           "The owner could not read the expected vehicle location.")

    response = send_request("GET", base_url, endpoint, visitor_token)
    data = read_json(response)
    outcome = "inconclusive"
    details = "Unexpected response; could not determine whether vehicle access was restricted."
    if response.status_code in (401, 403):
        outcome = "passed"
        details = "The API rejected this other-account request."
    elif (response.status_code == 200 and isinstance(data, dict)
          and data.get("carId") == vehicle_id
          and isinstance(data.get("vehicleLocation"), dict) and data["vehicleLocation"]):
        outcome = "finding"
        details = "A different account received this vehicle's location. Confirm the accounts do not share access."
    return make_result("BOLA", endpoint, outcome, response.status_code, details)


def rate_limiting(base_url, email, attempts):
    """Observe a small number of failed logins; do not claim unlimited access."""
    if not 0 <= attempts <= 20:
        raise ValueError("Rate-limit attempts must be between 0 and 20.")
    result = make_result("Rate Limiting", LOGIN_PATH, "skipped", None,
                         "Optional check. Use --rate-attempts 10 to enable it.")
    result["attempts_sent"] = 0
    for number in range(1, attempts + 1):
        try:
            response = send_request("POST", base_url, LOGIN_PATH,
                                    data={"email": email, "password": "scanner-deliberately-wrong-password"})
        except requests.RequestException:
            result.update(outcome="error", status_code=None,
                          details="A request failed; the server may have received the last attempt.")
            result["attempts_sent"] = number
            return result
        result["attempts_sent"] = number
        result["status_code"] = response.status_code
        if response.status_code == 429:
            result.update(outcome="passed", details="HTTP 429 observed: the API signaled too many requests.")
            return result
        if response.status_code not in (401, 403):
            result.update(outcome="inconclusive", details="Unexpected login response; stopped the check.")
            return result
    if attempts:
        result.update(outcome="inconclusive",
                      details=f"No HTTP 429 in {attempts} attempts. A higher threshold or another protection may exist.")
    return result


def run_all_tests(base_url, visitor_token, owner_token, visitor_email, attempts):
    # Each check is independent: a failed connection should not discard other results.
    results = []
    try:
        results.append(broken_auth(base_url, visitor_token))
    except requests.RequestException:
        results.append(make_result("Broken Authentication", DASHBOARD_PATH, "error", None,
                                   "Request failed. Check that crAPI is reachable."))
    try:
        results.append(bola(base_url, visitor_token, owner_token))
    except requests.RequestException:
        results.append(make_result("BOLA", VEHICLES_PATH, "error", None,
                                   "Request failed. Check that crAPI is reachable."))
    results.append(rate_limiting(base_url, visitor_email, attempts))
    return results


def print_report(results):
    print("\n=== SCAN REPORT ===\n")
    for result in results:
        status = result["status_code"]
        http = str(status) if status is not None else "not available"
        print(f"[{result['outcome'].upper()}] {result['check']} (HTTP {http})")
        print("  " + result["details"])
    findings = sum(result["outcome"] == "finding" for result in results)
    print(f"\n{findings} potential finding(s). A passed check is not a complete security assessment.")


def save_report(results, filename):
    # Store conclusions, not passwords, tokens, or raw personal data from responses.
    with open(filename, "w", encoding="utf-8") as report_file:
        json.dump(results, report_file, indent=4)
        report_file.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8888", help="crAPI target URL")
    parser.add_argument("--rate-attempts", type=int, default=0, help="Optional failed logins, from 0 to 20")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    url = urlsplit(base_url)
    if (url.scheme not in ("http", "https") or not url.hostname
            or url.username is not None or url.password is not None or url.query or url.fragment):
        parser.error("Use an HTTP(S) base URL without credentials, a query, or a fragment.")
    if not 0 <= args.rate_attempts <= 20:
        parser.error("--rate-attempts must be between 0 and 20.")

    print(f"Target: {base_url}")
    print("Use two separate test accounts. The owner account must have a vehicle.")
    try:
        visitor_email = os.getenv("SCANNER_VISITOR_EMAIL") or input("Visitor email: ").strip()
        visitor_password = os.getenv("SCANNER_VISITOR_PASSWORD") or getpass("Visitor password: ")
        owner_email = os.getenv("SCANNER_OWNER_EMAIL") or input("Owner email: ").strip()
        owner_password = os.getenv("SCANNER_OWNER_PASSWORD") or getpass("Owner password: ")
        if not all((visitor_email, visitor_password, owner_email, owner_password)):
            raise ValueError("Both accounts need an email and password.")
        if visitor_email.casefold() == owner_email.casefold():
            raise ValueError("Use two different accounts for the BOLA check.")
        visitor_token = login(base_url, visitor_email, visitor_password)
        owner_token = login(base_url, owner_email, owner_password)
        results = run_all_tests(base_url, visitor_token, owner_token, visitor_email, args.rate_attempts)
    except requests.RequestException:
        print("Could not complete login. Check that crAPI is running and the URL is correct.")
        return 1
    except (ValueError, EOFError) as error:
        print(f"Could not start scan: {error}")
        return 1

    print_report(results)
    report_path = Path(__file__).with_name("report.json")
    try:
        save_report(results, report_path)
    except OSError:
        print("Could not save report.json. Check the folder's write permissions.")
        return 1
    print(f"Saved report: {report_path}")
    return 0


# Importing this file for tests does not start network requests or ask for passwords.
if __name__ == "__main__":
    raise SystemExit(main())
