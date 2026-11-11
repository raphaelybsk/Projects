# Security & Systems Engineering Portfolio

A collection of hands-on projects built to develop real engineering depth in application security, DevSecOps, and backend/systems programming, built while transitioning from a Computer Science degree into a cybersecurity career.

The projects cover API access control, accidental credential exposure, and basic security event monitoring. Each project includes setup instructions, usage examples, and its current limitations.

---

## Projects

### 1. [API Security Scanner](./api-security-scanner)
**Stack:** Python, requests, OWASP crAPI test lab

A beginner command-line tool that checks authentication and access to another user's vehicle in a local crAPI lab, with an optional rate-limit check. Uses two test accounts, compares responses with working baselines, and saves readable JSON reports. Includes offline tests and documents the scope and limitations of each check.

### 2. [Secrets Scanner](./secrets-scanner)
**Stack:** Go

A Go command-line tool that scans local files and added lines in Git history for potential secrets. Combines regular expressions with Shannon entropy checks, masks matched values, and produces terminal output and an optional JSON report. Findings require manual review; live credential validation, SARIF output, and pre-commit integration are not implemented.

### 3. [SIEM Dashboard](./siem-dashboard)
**Stack:** Python/FastAPI, SQLite, HTML, CSS, JavaScript

A beginner security monitoring project that imports example JSON logs, stores events in SQLite, and displays them in a simple web dashboard. Includes a severity filter and one rule that finds five failed logins from the same IP within five minutes. Uses plain HTML, CSS, and JavaScript, with a local FastAPI server and sample events for demonstration.

---

## Purpose

This repository serves as a technical portfolio demonstrating engineering ability across application security, DevSecOps automation, and systems-level programming.
