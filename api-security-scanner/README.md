# API Security Scanner

A small Python command-line tool that checks three API security behaviors in a local [OWASP crAPI](https://github.com/OWASP/crAPI) lab. Built as a beginner learning project using ordinary functions, dictionaries, loops, and the `requests` library.

Inspired by the [API Security Scanner project](https://github.com/CarterPerez-dev/Cybersecurity-Projects/tree/main/PROJECTS/intermediate/api-security-scanner). This version focuses on understanding the scanner itself. It does not implement the reference project's full web application or the whole OWASP API Security Top 10.

## What it does

- **Broken Authentication:** checks that a logged-in user can read a dashboard, then requests it without a token.
- **BOLA / IDOR:** verifies two different user identities, gets the owner's first vehicle, checks that the owner can read its location, then tries that same vehicle with the visitor's token.
- **Rate Limiting:** sends a small number of failed logins and looks for HTTP `429` (too many requests).
- Prints understandable conclusions and saves them in `report.json`.

Passwords are entered through hidden terminal prompts. Every request has a 10-second connection/read timeout, and redirects are not followed. Reports omit passwords, tokens, and raw response bodies; they still contain the tested endpoint, including a vehicle ID for BOLA.

## Requirements

- Python 3.11 or newer
- crAPI running locally, normally at `http://localhost:8888`
- Two separate test accounts in crAPI
- A vehicle belonging to the **owner** account, with no legitimate shared access for the **visitor**

Docker is needed if you use crAPI's Docker setup. The scanner itself needs only Python and `requests`.

## Setup

Open a terminal in `api-security-scanner`, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Usage

Start crAPI, register your two test accounts, and add a vehicle to the owner account through crAPI. Then run:

```bash
python scanner.py
```

Enter the visitor's email and password, followed by the owner's email and password. Nothing appears while you type a password; that is normal. You do not need to edit the Python file.

By default, the scanner runs the authentication and BOLA checks and marks rate limiting as `skipped`. To include ten failed login attempts:

```bash
python scanner.py --rate-attempts 10
```

The allowed range is 0–20. This check uses the visitor account and can trigger protections such as an account lockout, so use a disposable lab account. It stops at the first `429` or unexpected response. There is no retry loop or deliberate delay between attempts.

For a different crAPI address:

```bash
python scanner.py --base-url http://localhost:8889
```

The endpoint paths and expected JSON fields are specific to crAPI. Changing the base URL does not make this a generic API scanner.

For repeated use, you can optionally supply credentials using these environment variables:

- `SCANNER_VISITOR_EMAIL`
- `SCANNER_VISITOR_PASSWORD`
- `SCANNER_OWNER_EMAIL`
- `SCANNER_OWNER_PASSWORD`

A missing variable falls back to a prompt. The script does not automatically load a `.env` file. Hidden prompts are the simplest way to get started.

## Understanding the report

| Outcome | Meaning |
| --- | --- |
| `finding` | Expected user or vehicle fields were returned where access should be restricted. Review the result. |
| `passed` | The API rejected this particular access attempt, or signaled rate limiting with `429`. |
| `inconclusive` | The response or setup was insufficient to reach a conclusion. |
| `error` | A request failed, for example because of a timeout or connection problem. |
| `skipped` | The optional check was not requested. |

A `404` is **inconclusive**, because it may mean a wrong route, missing resource, or deliberate access concealment. A `200` without the expected JSON fields is also inconclusive. No `429` after a few failed logins does **not** prove that rate limiting is absent.

Example terminal headings (illustrative, not results from your lab):

```text
[INCONCLUSIVE] Broken Authentication (HTTP 404)
[FINDING] BOLA (HTTP 200)
[SKIPPED] Rate Limiting (HTTP not available)
```

See [report.example.json](./report.example.json) for fictional sample output. Actual results depend on your crAPI version and account setup.

Each completed scan overwrites `report.json` beside `scanner.py`. If login fails, no new report is written and any previous report stays in place. The terminal explains the problem. A successful run exits with code 0 even when findings or individual check errors exist; this is an interactive learning tool, not a CI security gate.

## Project files

```text
api-security-scanner/
├── scanner.py           # Requests, checks, terminal output, and JSON saving
├── requirements.txt     # One external dependency: requests
├── test_scanner.py      # Offline tests using fake responses
├── report.example.json  # Fictional sample report
├── LEARNING.md          # Function-by-function explanation and exercises
├── README.md
└── .gitignore           # Excludes generated reports and local files
```

Start with [LEARNING.md](./LEARNING.md), then read `scanner.py` one function at a time.

## Tests

With the virtual environment activated:

```bash
python -m unittest -v test_scanner.py
```

Tests use Python's built-in `unittest` and replace HTTP requests with fake responses. They do not contact crAPI, require credentials, or overwrite your report. They check the scanner's decisions; they do not prove the behavior of a live target.

## Why this matters

Authentication asks **who you are**. Authorization asks **which resources you may access**. A valid login token does not mean a user should be able to read another user's vehicle. Comparing requests with different identities makes that distinction concrete.

## Status and limitations

This is a small learning project. It tests one dashboard endpoint, one vehicle, and optionally a short series of login failures. A passed check does not establish that the API is secure. Findings need manual review, especially if the application legitimately shares resources between accounts.

It does not crawl endpoints, discover every authorization rule, test SQL injection, refresh expired tokens, measure throttling delays, or store scan history. There is no web dashboard or database.

Possible next exercises:

- Add a timestamp to the report.
- Add an invalid-token authentication check.
- Explain and test another unexpected HTTP response.
- Add a simple web interface after you can explain the existing request flow.

## Disclaimer

Use this tool only against systems you own or have explicit permission to test, such as your local crAPI lab.
