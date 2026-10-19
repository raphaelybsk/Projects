"""Offline tests: fake HTTP responses, no running crAPI or accounts needed."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

import scanner

BASE_URL = "http://localhost:8888"
VEHICLE_ID = "example-vehicle"
LOCATION = {"carId": VEHICLE_ID, "vehicleLocation": {"latitude": "1", "longitude": "2"}}


def response(status, data=None):
    fake = Mock(status_code=status)
    fake.json.return_value = data
    return fake


def bola_responses(final_response):
    return [
        response(200, {"id": 1}),
        response(200, {"id": 2}),
        response(200, [{"uuid": VEHICLE_ID}]),
        response(200, LOCATION),
        final_response,
    ]


class ScannerTests(unittest.TestCase):
    @patch("scanner.requests.request")
    def test_requests_use_timeout_and_do_not_follow_redirects(self, request):
        scanner.send_request("GET", BASE_URL, "/example", "test-token")
        self.assertEqual(request.call_args.kwargs["timeout"], 10)
        self.assertFalse(request.call_args.kwargs["allow_redirects"])
        self.assertEqual(request.call_args.kwargs["headers"], {"Authorization": "Bearer test-token"})

    @patch("scanner.send_request")
    def test_login_requires_a_successful_response_and_token(self, request):
        for status, data in [(401, {}), (200, {}), (200, []), (200, {"token": 123})]:
            with self.subTest(status=status, data=data):
                request.return_value = response(status, data)
                with self.assertRaises(ValueError):
                    scanner.login(BASE_URL, "test@example.test", "test-password")
        request.return_value = response(200, {"token": "valid-token"})
        self.assertEqual(scanner.login(BASE_URL, "test@example.test", "test-password"), "valid-token")

    @patch("scanner.send_request")
    def test_authentication_distinguishes_rejection_from_unknown_responses(self, request):
        for status, outcome in [(401, "passed"), (403, "passed"), (404, "inconclusive"),
                                (500, "inconclusive"), (302, "inconclusive"), (200, "inconclusive")]:
            with self.subTest(status=status):
                request.side_effect = [response(200, {"id": 1, "email": "user@example.test"}), response(status, {})]
                result = scanner.broken_auth(BASE_URL, "visitor-token")
                self.assertEqual(result["outcome"], outcome)
                self.assertEqual(result["status_code"], status)

    @patch("scanner.send_request")
    def test_authentication_requires_working_baseline(self, request):
        request.return_value = response(404)
        self.assertEqual(scanner.broken_auth(BASE_URL, "token")["outcome"], "inconclusive")
        request.assert_called_once()

    @patch("scanner.send_request")
    def test_anonymous_dashboard_is_a_finding_without_saving_personal_data(self, request):
        dashboard = {"id": 1, "email": "private@example.test"}
        request.side_effect = [response(200, dashboard), response(200, dashboard)]
        result = scanner.broken_auth(BASE_URL, "token")
        self.assertEqual(result["outcome"], "finding")
        self.assertNotIn("private@example.test", json.dumps(result))

    @patch("scanner.send_request")
    def test_bola_requires_the_same_vehicle_in_the_response(self, request):
        for data, outcome in [(LOCATION, "finding"), ({}, "inconclusive"),
                              ({"carId": "other-vehicle", "vehicleLocation": {"id": 1}}, "inconclusive")]:
            with self.subTest(data=data):
                request.side_effect = bola_responses(response(200, data))
                result = scanner.bola(BASE_URL, "visitor-token", "owner-token")
                self.assertEqual(result["outcome"], outcome)
                self.assertNotIn("latitude", json.dumps(result))
                self.assertEqual(request.call_args.args[-1], "visitor-token")

    @patch("scanner.send_request")
    def test_bola_rejections_and_missing_routes(self, request):
        for status, outcome in [(401, "passed"), (403, "passed"), (404, "inconclusive"), (500, "inconclusive")]:
            with self.subTest(status=status):
                request.side_effect = bola_responses(response(status))
                self.assertEqual(scanner.bola(BASE_URL, "visitor", "owner")["outcome"], outcome)

    @patch("scanner.send_request")
    def test_bola_stops_for_same_account_missing_vehicle_or_failed_baseline(self, request):
        cases = [
            [response(200, {"id": 1}), response(200, {"id": 1})],
            [response(200, {"id": 1}), response(200, {"id": 2}), response(200, [])],
            bola_responses(response(200, LOCATION))[:3] + [response(404)],
        ]
        for replies in cases:
            with self.subTest(replies=len(replies)):
                request.reset_mock()
                request.side_effect = replies
                self.assertEqual(scanner.bola(BASE_URL, "visitor", "owner")["outcome"], "inconclusive")
                self.assertEqual(request.call_count, len(replies))

    @patch("scanner.send_request")
    def test_rate_limit_stops_at_429_and_counts_actual_attempts(self, request):
        request.side_effect = [response(401), response(429)]
        result = scanner.rate_limiting(BASE_URL, "test@example.test", 10)
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["attempts_sent"], 2)
        self.assertEqual(request.call_count, 2)

    @patch("scanner.send_request")
    def test_no_429_is_not_proof_of_a_vulnerability(self, request):
        request.return_value = response(401)
        result = scanner.rate_limiting(BASE_URL, "test@example.test", 3)
        self.assertEqual(result["outcome"], "inconclusive")
        self.assertEqual(result["attempts_sent"], 3)

    @patch("scanner.send_request")
    def test_rate_limit_skipped_or_invalid_sends_no_requests(self, request):
        self.assertEqual(scanner.rate_limiting(BASE_URL, "email", 0)["outcome"], "skipped")
        for attempts in (-1, 21):
            with self.assertRaises(ValueError):
                scanner.rate_limiting(BASE_URL, "email", attempts)
        request.assert_not_called()

    @patch("scanner.send_request")
    def test_rate_limit_stops_on_unexpected_status_or_connection_error(self, request):
        for reply, outcome in [(response(200), "inconclusive"), (response(500), "inconclusive"),
                               (requests.Timeout(), "error")]:
            with self.subTest(outcome=outcome):
                request.reset_mock()
                request.side_effect = [reply]
                result = scanner.rate_limiting(BASE_URL, "email", 3)
                self.assertEqual(result["outcome"], outcome)
                self.assertEqual(result["attempts_sent"], 1)
                request.assert_called_once()

    @patch("scanner.send_request", side_effect=requests.ConnectionError)
    def test_connection_errors_are_reported_and_other_checks_continue(self, request):
        results = scanner.run_all_tests(BASE_URL, "visitor", "owner", "email", 0)
        self.assertEqual([item["outcome"] for item in results], ["error", "error", "skipped"])

    def test_html_response_does_not_crash_json_parsing(self):
        html_response = Mock()
        html_response.json.side_effect = ValueError("Not JSON")
        self.assertIsNone(scanner.read_json(html_response))

    def test_report_is_readable_json(self):
        results = [scanner.make_result("BOLA", "/example", "inconclusive", 404, "Not found")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.json"
            scanner.save_report(results, path)
            self.assertEqual(json.loads(path.read_text()), results)


if __name__ == "__main__":
    unittest.main()
