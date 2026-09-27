# Security & Systems Engineering Portfolio

A collection of hands-on projects built to develop real engineering depth in application security, DevSecOps, and backend/systems programming — built while transitioning from a Computer Science degree into a cybersecurity career.

Each project is designed to demonstrate a specific, real-world engineering problem rather than follow a tutorial: from finding vulnerabilities in live APIs to building a database engine from first principles.

---

## Projects

### 1. API Security Scanner
**Stack:** FastAPI, React/TypeScript, Docker | **Time:** 3-5 days

A tool that scans REST and GraphQL/SOAP APIs for common security vulnerabilities, based on the OWASP API Security Top 10. Includes automated fuzzing (with ML-assisted payload generation), detection for BOLA/IDOR, broken authentication, and injection flaws, and generates structured vulnerability reports. Built with a FastAPI backend and a React dashboard for reviewing scan results.

### 2. Secrets Scanner
**Stack:** Go | **Time:** 1-2 days

A CLI tool that scans repositories and full Git history for accidentally committed secrets — API keys, tokens, credentials. Uses regex pattern matching combined with Shannon entropy analysis to reduce false positives, with optional live validation against known services (e.g. HaveIBeenPwned k-anonymity checks). Outputs SARIF-compatible reports for CI/CD integration and supports pre-commit hook usage.

### 3. SIEM Dashboard
**Stack:** Flask, React | **Time:** 3-5 days

A lightweight Security Information and Event Management dashboard that ingests logs from multiple sources, correlates events, and surfaces potential security incidents in real time. Includes basic detection rules, alerting, and a React frontend for log search and visualization — modeling the core workflow of a SOC analyst's daily tooling.

### 4. Docker Security Audit
**Stack:** Go | **Time:** 1-2 days

A command-line auditing tool that scans Docker containers and images against CIS Docker Benchmark controls — checking for misconfigurations, excessive privileges, exposed secrets, and insecure defaults. Produces a prioritized findings report to help harden containerized environments.

### 5. SBOM Generator & Vulnerability Matcher
**Stack:** Go | **Time:** 2-4 days

A tool that generates a Software Bill of Materials (SBOM) for a codebase or container image and cross-references dependencies against known CVE databases. Aimed at supply-chain security — helping identify vulnerable or outdated packages before they ship to production.

### 6. Cloud Security Compliance Dashboard
**Stack:** Go, React, AWS | **Time:** 2-3 weeks

A dashboard that audits AWS infrastructure against common compliance frameworks (e.g. CIS AWS Foundations Benchmark), flagging misconfigured IAM policies, open security groups, unencrypted storage, and other cloud security risks. Combines a Go-based scanning engine with a React frontend for visualizing compliance posture over time.

### 7. Build-Your-Own Database
**Stack:** Go | **Time:** 3-6 weeks

A persistent, from-scratch database engine implementing B-tree indexing, a query executor, transaction support, concurrent access control, and crash recovery. Built to gain a deep, practical understanding of how databases work internally — storage engines, indexing strategies, and consistency guarantees — rather than just using one.

### 8. Binary Analysis Tool
**Stack:** Rust | **Time:** 3-5 days

A static/dynamic binary analysis tool for inspecting executables — parsing binary formats (ELF/PE), extracting strings and metadata, identifying suspicious patterns, and providing basic disassembly output. A foundation for reverse engineering and malware analysis work.

---

## Purpose

This repository serves as a technical portfolio demonstrating engineering ability across application security, DevSecOps automation, and systems-level programming — the range of skills relevant to both software engineering and cybersecurity roles.
