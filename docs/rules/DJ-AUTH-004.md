# DJ-AUTH-004: CSRF protection disabled (@csrf_exempt)

[Back to the rules catalog](index.md)

## What it detects

CSRF protection is turned off. An external site can make an authenticated user's browser run this operation without the user knowing.

## How to fix it

Remove csrf_exempt and send the CSRF token from the client. For APIs consumed by other systems, use token authentication instead of sessions.

## Why it matters

This rule maps to [CWE-352](https://cwe.mitre.org/data/definitions/352.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check whether the action changes data and whether it requires an anti-CSRF token or a SameSite cookie. In testing, send the request from another site.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | ACCESS CONTROL |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-352](https://cwe.mitre.org/data/definitions/352.html) |
| OWASP | A01:2025 Broken Access Control |
