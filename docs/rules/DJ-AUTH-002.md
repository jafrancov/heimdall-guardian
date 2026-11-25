# DJ-AUTH-002: View without authentication (Django, CBV)

[Back to the rules catalog](index.md)

## What it detects

Class-based view without LoginRequiredMixin or PermissionRequiredMixin. If it is published in urls.py, it is reachable without logging in.

## How to fix it

Inherit from LoginRequiredMixin or PermissionRequiredMixin as the first base class. If the view must be public, document it and accept the finding with a justification.

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
