# Secrets Scanner

A command-line tool that finds hardcoded secrets (API keys, tokens, private keys, passwords) in source code and in git history. Written in Go as a hands-on way to learn both the language and how secrets leak in real repositories.

## What it does

The scanner combines two detection methods:

- **Pattern rules** — regular expressions for well-known credential formats (AWS access keys, GitHub tokens, private key headers, and similar).
- **Entropy analysis** — flags high-entropy strings that look random enough to be keys, even when no rule matches.

It scans two sources:

- **Working directory** — every text file under a given path, skipping binaries and `.git`.
- **Git history** — past commits, to catch secrets that were committed and later "deleted" but still live in the history.

Each finding reports the file, line, commit (for history scans) and the type of secret. Matched values are masked in the output so the report itself does not leak the secret.

## Requirements

- Go 1.22+
- Git installed and available in your `PATH` (needed for history scans)

## Setup

```bash
git clone https://github.com/raphaelybsk/secrets-scanner.git
cd secrets-scanner
go build -o secrets-scanner .
```

## Usage

Planned interface:

```bash
./secrets-scanner --path ./some-repo            # scan current files
./secrets-scanner --path ./some-repo --git      # also scan git history
./secrets-scanner --path ./some-repo --json report.json
```

Target output format:

```
=== SECRETS REPORT ===

[HIGH] AWS Access Key — config/settings.py:12 (AKIA************MPLE)
[HIGH] Private Key — deploy/id_rsa:1 (commit a1b2c3d)
[MEDIUM] High-entropy string — app/utils.py:48

3 potential secrets found.
```

## Why this matters

Leaked credentials in repositories are one of the most common causes of real-world breaches, and deleting a secret from the latest commit does not remove it from history. This project is a hands-on way to understand how detection tools work by building the core of one: rules, entropy, and history traversal.

## Status

Early-stage learning project, currently in development. Scope for v1:

- Directory scan with pattern rules
- Entropy-based detection
- Git history scan
- Terminal report and JSON output

Planned next steps: allowlist/baseline file to silence known false positives, pre-commit hook, and a GitHub Actions workflow.

## Disclaimer

This tool is intended for scanning repositories you own or have explicit permission to analyse. Do not use it against code or systems without authorization.