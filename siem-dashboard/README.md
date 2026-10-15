# SIEM Dashboard

A small web application that stores security events and looks for repeated failed logins. Built with Python, FastAPI, SQLite, and plain HTML, CSS, and JavaScript as a beginner learning project.

## What it does

- Add a test event using a form in the browser.
- Import example events from a JSON file.
- Save events in a local SQLite database.
- Display the latest 100 matching events and filter them by severity.
- Show an alert when one IP has five or more failed logins in the last five minutes.

This is a small first version of a SIEM, not the complete system in the original project plan.

## Requirements

- Python 3.11 or newer
- A web browser

You do not need Node.js, npm, React, Docker, or a separate database server.

## Setup

Open a terminal in `siem-dashboard`, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The activation command above is for macOS/Linux. On Windows PowerShell, use `.venv\Scripts\Activate.ps1`.

## Usage

Start the server:

```bash
python app.py
```

Open [the dashboard](http://127.0.0.1:8000) in your browser. The Python server also serves the frontend, so only one server is needed. There is no build command or login screen.

To load the example events, open a second terminal in the same folder:

```bash
source .venv/bin/activate
python import_logs.py
```

Click **Refresh** in the dashboard. On a new database, you should see **7 events and 1 alert**. The IP addresses and messages are fictional.

You can also use **Add a test event**. With the default values, clicking **Add event** five times creates five failed logins from the same IP. The severity filter affects the table, but not the alerts.

The server assigns the current UTC time when each event is added. Alerts are calculated when you refresh: they disappear once fewer than five matching events remain in the five-minute window. Events stay in the database. Importing the file again adds the same events again; duplicates are not detected.

Use Ctrl+C in the server terminal to stop it. Changes to Python code require restarting the server. Changes to HTML, CSS, or JavaScript require refreshing the browser.

## Project files

```text
siem-dashboard/
├── app.py              # Python server, API, SQL, and detection rule
├── import_logs.py      # Sends the sample logs to the API
├── sample_logs.json    # Seven example events
├── requirements.txt    # Python packages to install
├── static/
│   ├── index.html      # Page structure
│   ├── style.css       # Page appearance
│   └── script.js       # Fetches data and updates the page
├── test_app.py         # Small backend tests
├── LEARNING.md         # Explanations and study order
├── README.md
└── .gitignore          # Generated files that Git should ignore
```

## Tests

Tests are optional for running the dashboard. To run them, activate `.venv` and install the test helper:

```bash
python -m pip install httpx
python -m unittest -v test_app.py
```

The tests use a temporary database, so they do not change your saved events. They check validation, filtering, storage, and the failed-login rule.

## Why this matters

Individual logs tell you what happened. Looking at several related logs can reveal a pattern. This project demonstrates that basic idea by grouping recent failed logins by IP address.

An alert does not prove an attack. Someone repeatedly entering an incorrect password can trigger the same rule.

## Status

Beginner learning project with a working local dashboard. The code uses ordinary functions, loops, a small data model, and direct SQL queries.

To keep this version small, it does not include authentication, network syslog receivers, React, charts, configurable rules, alert history, export, or external notifications. It listens only on `127.0.0.1`. Keep it on your own computer; it has no access control and is not intended for public deployment.

Project possible improvements:

- Add a source-IP filter.
- Change the failed-login threshold and explain the result.
- Add a second simple detection rule.
- Add a small chart after understanding the table and JavaScript.

## Disclaimer

Use synthetic logs or logs from systems you own or are authorized to inspect. Do not put passwords or personal data in public examples.
