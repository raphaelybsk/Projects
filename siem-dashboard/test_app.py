import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        # Each test uses an empty database in a temporary folder.
        self.folder = tempfile.TemporaryDirectory()
        self.original_database = app.DATABASE
        app.DATABASE = Path(self.folder.name) / "test.db"
        app.create_table()
        self.client = TestClient(app.app)
        self.event = {
            "source": "ssh",
            "source_ip": "198.51.100.42",
            "event_type": "login_failed",
            "severity": "medium",
            "message": "Failed login for alice",
        }

    def tearDown(self):
        self.client.close()
        app.DATABASE = self.original_database
        self.folder.cleanup()

    def test_save_and_filter_events(self):
        response = self.client.post("/api/events", json=self.event)
        self.assertEqual(response.status_code, 201)
        events = self.client.get("/api/events?severity=medium").json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["message"], self.event["message"])
        self.assertTrue(events[0]["timestamp"])
        self.assertEqual(self.client.get("/api/events?severity=high").json(), [])

    def test_fifth_failure_triggers_alert(self):
        for number in range(4):
            self.client.post("/api/events", json=self.event)
        self.assertEqual(self.client.get("/api/alerts").json(), [])
        self.client.post("/api/events", json=self.event)
        alerts = self.client.get("/api/alerts").json()
        self.assertEqual(alerts, [{"source_ip": "198.51.100.42", "failed_logins": 5}])

    def test_different_ips_do_not_share_a_count(self):
        for number in range(5):
            self.event["source_ip"] = f"192.0.2.{number + 1}"
            self.client.post("/api/events", json=self.event)
        self.assertEqual(self.client.get("/api/alerts").json(), [])

    def test_successful_logins_do_not_count(self):
        self.event["event_type"] = "login_success"
        for number in range(5):
            self.client.post("/api/events", json=self.event)
        self.assertEqual(self.client.get("/api/alerts").json(), [])

    def test_old_events_do_not_count(self):
        for number in range(5):
            self.client.post("/api/events", json=self.event)
        connection = app.connect_database()
        connection.execute("UPDATE events SET timestamp = datetime('now', '-6 minutes')")
        connection.commit()
        connection.close()
        self.assertEqual(self.client.get("/api/alerts").json(), [])
        self.assertEqual(len(self.client.get("/api/events").json()), 5)

    def test_invalid_input_is_rejected(self):
        for field, value in [("source_ip", "invalid"), ("severity", "urgent"), ("message", "")]:
            invalid_event = self.event.copy()
            invalid_event[field] = value
            response = self.client.post("/api/events", json=invalid_event)
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/api/events").json(), [])

    def test_page_and_static_files_are_available(self):
        for path in ["/", "/static/script.js", "/static/style.css"]:
            self.assertEqual(self.client.get(path).status_code, 200)


if __name__ == "__main__":
    unittest.main()
