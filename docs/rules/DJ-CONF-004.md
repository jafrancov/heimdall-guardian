# DJ-CONF-004: Insecure cookies or transport in settings

[Back to the rules catalog](index.md)

## What it detects

Session or CSRF cookies without the Secure flag, or HTTPS redirection turned off: session credentials can travel in clear text.

## How to fix it

In production: SESSION_COOKIE_SECURE = True, CSRF_COOKIE_SECURE = True and SECURE_SSL_REDIRECT = True, plus SECURE_HSTS_SECONDS.

## Why it matters

This rule maps to [CWE-614](https://cwe.mitre.org/data/definitions/614.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Check the session cookie's attributes: it should carry `Secure` and `HttpOnly`. Confirm it in the browser's developer tools.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | CONFIGURATION |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-614](https://cwe.mitre.org/data/definitions/614.html) |
| OWASP | A02:2025 Security Misconfiguration |
