# PHP-CONF-001: display_errors on or credentials in a versioned .env

[Back to the rules catalog](index.md)

## What it detects

Insecure configuration: display_errors turned on (shows paths, queries and stack traces to any visitor) or credentials written in a versioned .env file.

## How to fix it

In production, set display_errors = Off and log_errors = On. Do not version the .env file: add it to .gitignore, keep a .env.example without values and change the exposed credentials.

## Why it matters

This rule maps to [CWE-209](https://cwe.mitre.org/data/definitions/209.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Cause an error in a test environment and check whether the response shows paths, queries or traces. Production should only show a generic message.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | CONFIGURATION |
| Stack | PHP and Laravel |
| Languages | `regex` |
| CWE | [CWE-209](https://cwe.mitre.org/data/definitions/209.html) |
| OWASP | A02:2025 Security Misconfiguration |
