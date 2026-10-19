# Security & Systems Engineering Portfolio

A collection of hands-on projects built to develop real engineering depth in application security, DevSecOps, and backend/systems programming, built while transitioning from a Computer Science degree into a cybersecurity career.

Each project is designed to demonstrate a specific, real-world engineering problem rather than follow a tutorial: from finding vulnerabilities in live APIs to building a database engine from first principles.

---

## Projects

### 1. [API Security Scanner](./api-security-scanner)
**Stack:** Python, requests, OWASP crAPI test lab

A beginner command-line tool that checks authentication and access to another user's vehicle in a local crAPI lab, with an optional rate-limit check. Uses two test accounts, compares responses with working baselines, and saves readable JSON reports. Includes offline tests and a guide explaining the code and its limitations.

### 2. Secrets Scanner
**Stack:** Go

A CLI tool that scans repositories and full Git history for accidentally committed secrets — API keys, tokens, credentials. Uses regex pattern matching combined with Shannon entropy analysis to reduce false positives, with optional live validation against known services (e.g. HaveIBeenPwned k-anonymity checks). Outputs SARIF-compatible reports for CI/CD integration and supports pre-commit hook usage.

### 3. [SIEM Dashboard](./siem-dashboard)
**Stack:** Python/FastAPI, SQLite, HTML, CSS, JavaScript

A beginner security monitoring project that imports example JSON logs, stores events in SQLite, and displays them in a simple web dashboard. Includes a severity filter and one rule that finds five failed logins from the same IP within five minutes. Uses plain HTML, CSS, and JavaScript, with a short guide explaining how the pieces work.

---

## Purpose

This repository serves as a technical portfolio demonstrating engineering ability across application security, DevSecOps automation, and systems-level programming.
