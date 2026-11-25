# DJ-CONF-002: Literal SECRET_KEY in the code

[Back to the rules catalog](index.md)

## What it detects

SECRET_KEY written as a literal in the code. Anyone with access to the repository can forge sessions, password reset tokens and signed data.

## How to fix it

Generate a new key, load it from an environment variable or a secrets manager, and treat the one left in the repository as compromised.

## Why it matters

This rule maps to [CWE-798](https://cwe.mitre.org/data/definitions/798.html) and to the OWASP Top 10:2025 category A07:2025 Authentication Failures.

## How to verify it

Look for the value in the version history and confirm whether it is still valid. If it is, rotate it right away and move it to a secrets manager.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Authentication Failures |
