# DJ-AUTH-001: View without authentication (Django, FBV)

[Back to the rules catalog](index.md)

## What it detects

Function-based view without an authentication or permission decorator. If it is published in urls.py, anyone can call it without logging in.

## How to fix it

Add @login_required or @permission_required. If the view must be public (for example, the login page), document it and accept the finding with a justification.

## Why it matters

This rule maps to [CWE-306](https://cwe.mitre.org/data/definitions/306.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check the route and its decorators, middleware or global filters. Send the request without credentials in a test environment: it should answer 401 or 403.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | LOW |
| Category | ACCESS CONTROL |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Broken Access Control |
