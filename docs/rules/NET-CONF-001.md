# NET-CONF-001: Password in connection string (.NET)

[Back to the rules catalog](index.md)

## What it detects

Connection string with the password written in a versioned configuration file. Anyone with access to the repository has access to the database.

## How to fix it

Change the password and take it out of the file: environment variables, User Secrets in development or a secrets manager in production.

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
| Stack | .NET |
| Languages | `regex` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Authentication Failures |
