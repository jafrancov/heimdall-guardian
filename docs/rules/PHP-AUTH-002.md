# PHP-AUTH-002: Route without authentication middleware (Laravel)

[Back to the rules catalog](index.md)

## What it detects

Laravel route declared outside a group with authentication middleware: it is reachable without logging in.

## How to fix it

Declare the route inside Route::middleware('auth')-&gt;group(...) or chain -&gt;middleware('auth'). If it must be public, document it and accept the finding with a justification.

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
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Broken Access Control |
