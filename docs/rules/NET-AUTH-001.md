# NET-AUTH-001: Controller without [Authorize] (.NET)

[Back to the rules catalog](index.md)

## What it detects

Controller without [Authorize] on the class or on its actions. Unless a global authorization filter exists, its actions are reachable without logging in.

## How to fix it

Add [Authorize] to the controller, or configure a global authorization policy (FallbackPolicy) and mark only what must be public with [AllowAnonymous].

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
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Broken Access Control |
