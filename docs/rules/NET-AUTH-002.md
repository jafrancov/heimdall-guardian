# NET-AUTH-002: Anonymous write action ([AllowAnonymous])

[Back to the rules catalog](index.md)

## What it detects

Write action (POST, PUT, PATCH or DELETE) marked with [AllowAnonymous]: anyone can modify data without authenticating.

## How to fix it

Remove [AllowAnonymous] and require authentication. If it must be public (for example, login), document it and accept the finding with a justification.

## Why it matters

This rule maps to [CWE-306](https://cwe.mitre.org/data/definitions/306.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check the route and its decorators, middleware or global filters. Send the request without credentials in a test environment: it should answer 401 or 403.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | ACCESS CONTROL |
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Broken Access Control |
