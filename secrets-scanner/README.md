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

- Go 1.27.2 or newer (as declared in `go.mod`)
- Git installed and available in your `PATH` (needed for history scans)

## Setup

```bash
git clone https://github.com/raphaelybsk/Projects.git
cd Projects/secrets-scanner
go build -o secrets-scanner .
```

## Usage

Run from the `secrets-scanner` directory:

```bash
./secrets-scanner --path ./some-repo            # scan current files
./secrets-scanner --path ./some-repo --git      # also scan git history
./secrets-scanner --path ./some-repo --json report.json
```

Illustrative output format:

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

Early-stage learning project. Currently implemented:

- Directory scan with pattern rules
- Entropy-based detection
- Git history scan
- Terminal report and JSON output

Known limitations: pattern and entropy checks can produce false positives and miss unknown secret formats. Git history scanning examines added diff lines returned by `git log -p --all`, rather than reconstructing every historical file. The tool does not validate whether credentials are active and does not implement SARIF output or a CI failure policy.

Planned next steps: allowlist/baseline support, automated tests, pre-commit integration, and a GitHub Actions workflow.

## Disclaimer

This tool is intended for scanning repositories you own or have explicit permission to analyse. Do not use it against code or systems without authorization.
