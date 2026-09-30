import requests
import json

# POST request to get a login token given an email and a password 
def login(email, password):
    login_info = {"email":email, "password":password}
    response = requests.post("http://localhost:8888/identity/api/auth/login", json=login_info)
    if response.status_code == 200:
        return response.json()["token"] 
    else:
        return None

# bubble login token
bubble_token = login("bubble@gmail.com", "Bubble123#")
# bubble2 login token
bubble2_token = login("bubble2@gmail.com", "Bubble123#")

# bubble header with his login token
bubble_header = {"Authorization": "Bearer " + bubble_token}
# bubble2 header with his login token
bubble2_header = {"Authorization": "Bearer " + bubble2_token}

# GET request to get user's dashboard info given a header
def dashboard_info(user_header):
    response = requests.get("http://localhost:8888/identity/api/v2/user/dashboard", headers=user_header)
    if response.status_code == 200:
        return "User's Dashboard: " + str(response.json())
    else:
        return None

# bubble's info
# bubble_info = dashboard_info(bubble_header)
# bubble2's info
# bubble2_info = dashboard_info(bubble2_header)

# GET request to get an user's vehicle UUID given his header 
def vehicle_uuid(user_header):
    response = requests.get("http://localhost:8888/identity/api/v2/vehicle/vehicles", headers=user_header)
    if response.status_code == 200:
        return str(response.json()[0]["uuid"])
    else:
        return None

# bubble2's vehicle UUID
bubble2_vehicle_uuid = vehicle_uuid(bubble2_header)

# GET request to test BOLA (broken object level authorization) - try to get someone elses vehicle's info while logged in in your own account
def bola(user_header, vehicle_uuid):
    response = requests.get("http://localhost:8888/identity/api/v2/vehicle/" + vehicle_uuid + "/location", headers=user_header)
    # print(response.status_code)
    if response.status_code == 200:
        return {"check": "BOLA", "endpoint": "/vehicle", "vulnerable": True, "status_code": response.status_code, "details":response.json()}
    else:
        return {"check": "BOLA", "endpoint": "/vehicle", "vulnerable": False, "status_code": response.status_code}

# GET request to test if we can get someone's info without being logged in (no headers)
def broken_auth():
    response = requests.get("http://localhost:8888/identity/api/v2/user/dashboard", headers={})
    # print(response.status_code)
    if response.status_code == 200:
        return {"check": "Broken Authentication", "endpoint": "/dashboard", "vulnerable": True, "status_code": response.status_code}
    else:
        return {"check": "Broken Authentication", "endpoint": "/dashboard", "vulnerable": False, "status_code": response.status_code}

# POST request to test if there is a limit of failed attempts to login
def rate_limiting(attempts):
    bad_login = {"email":"bubble@gmail.com", "password":"wrongPassword"}
    blocked = False
    for i in range(attempts):
        response = requests.post("http://localhost:8888/identity/api/auth/login", json=bad_login)
        if response.status_code == 429:
            blocked = True
            break

    return {"check": "Rate Limiting", "endpoint": "/login", "login attempts":attempts, "vulnerable": not blocked, "status_code": response.status_code}

def run_all_tests():
    results = []
    results.append(broken_auth())
    # getting bubble2's vehicle info logged in as bubble (bubble's header)
    results.append(bola(bubble_header, bubble2_vehicle_uuid))
    # testing 50 failed login attempts to see if it's possible to try as many times as we want (bruteforcing possible)
    results.append(rate_limiting(50))
    return results

all_results = run_all_tests()

def print_report(results):
    print("\n=== SCAN REPORT ===\n")
    for result in results:
        status = "VULNERABLE" if result["vulnerable"] else "OK"
        print(f"[{status}] {result['check']} — {result['endpoint']} (status {result['status_code']})")
    total = len(results)
    vulnerable_count = sum(1 for r in results if r["vulnerable"])
    print(f"\n{vulnerable_count}/{total} checks found vulnerable.\n")

def save_report(results, filename="report.json"):
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)

print_report(all_results)
save_report(all_results)
