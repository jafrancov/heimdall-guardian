# SWIFT-SEC-001: Hard-coded API key, secret or password (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Hard-coded secret: a constant named like an API key, secret, token or password is assigned a fixed string. Anyone who has the application (an IPA can be decrypted and inspected in minutes) or the repository can extract it.

## How to fix it

Remove the value from the code and rotate it if it was already published. A server secret must not ship in the application: use your own service that stores it. If it is a public client key, restrict it at the provider by bundle ID, and pass it with an .xcconfig file or a scheme outside the repository.

## Why it matters

This rule maps to [CWE-798](https://cwe.mitre.org/data/definitions/798.html) and to the OWASP Top 10:2025 category A07:2025 Authentication Failures.

## How to verify it

Look for the value in the version history and confirm whether it is still valid. If it is, rotate it right away and move it to a secrets manager.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Authentication Failures |
