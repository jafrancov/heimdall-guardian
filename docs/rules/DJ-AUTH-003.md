# DJ-AUTH-003: API without authentication: AllowAny (DRF)

[Back to the rules catalog](index.md)

## What it detects

Django REST Framework configured with AllowAny: the endpoint (or the whole API, if it is the default) accepts requests without authentication.

## How to fix it

Use IsAuthenticated or a specific permission. In settings, define DEFAULT_PERMISSION_CLASSES with IsAuthenticated and open only the endpoints that must be public.

## Why it matters

This rule maps to [CWE-306](https://cwe.mitre.org/data/definitions/306.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check the route and its decorators, middleware or global filters. Send the request without credentials in a test environment: it should answer 401 or 403.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | ACCESS CONTROL |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Broken Access Control |
