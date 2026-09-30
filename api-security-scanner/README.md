# API Security Scanner

A command-line tool that tests REST APIs for common security vulnerabilities from the OWASP API Security Top 10. Built against [OWASP crAPI](https://github.com/OWASP/crAPI) as a target for learning and testing purposes.

## What it does

The scanner currently checks for:

- **Broken Authentication** — attempts to access a protected endpoint without a valid token.
- **BOLA / IDOR (Broken Object Level Authorization)** — attempts to access another user's resource (in this case, vehicle location data) using a different user's valid token.

Each check reports whether the target is vulnerable, along with the HTTP status code returned.

## Requirements

- Python 3.11+
- [crAPI](https://github.com/OWASP/crAPI) running locally via Docker (or another target API with equivalent endpoints)
- Two registered user accounts on the target API, one of which owns a vehicle resource

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

## Usage

Update the credentials in `scanner.py` to match your test accounts, then run:

```bash
python3 scanner.py
```

This prints a summary to the terminal and saves full results to `report.json`. See [`report.example.json`](./report.example.json) for a sample output.

Example output:
```
=== SCAN REPORT ===

[OK] Broken Authentication — /dashboard (status 404)
[VULNERABLE] BOLA — /vehicle (status 200)
[VULNERABLE] Rate Limiting — /login (status 401)

2/3 checks found vulnerable.
```

## Why this matters

APIs are a common attack surface, and issues like BOLA and broken authentication account for a large share of real-world API breaches. This project is a hands-on way to understand how these vulnerabilities work by finding them manually first, then automating the detection.

## Status

This is an early-stage learning project, built as a hands-on introduction to API security testing. Current scope:

- 3 security checks implemented: Broken Authentication, BOLA/IDOR, and Rate Limiting
- Each check returns a structured result (endpoint, status code, vulnerable: true/false)
- Full results are saved to `report.json` after each run; a sample is available at [`report.example.json`](./report.example.json)

Known limitations: credentials are currently hard-coded for two fixed test accounts, and checks target specific crAPI endpoints rather than being generic across arbitrary APIs.

Planned next steps: move credentials to environment variables, restructure into a proper Python module, and eventually build a FastAPI backend with a web dashboard.

## Disclaimer

This tool is intended for testing systems you own or have explicit permission to test, such as intentionally vulnerable applications like crAPI. Do not use it against systems without authorization.