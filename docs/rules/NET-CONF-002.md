# NET-CONF-002: Insecure web.config (customErrors, debug, validateRequest)

[Back to the rules catalog](index.md)

## What it detects

ASP.NET configuration that is insecure for production: detailed errors visible, compilation in debug mode or request validation turned off.

## How to fix it

Use customErrors mode="RemoteOnly" or "On", compilation debug="false" and keep validateRequest enabled.

## Why it matters

This rule maps to [CWE-16](https://cwe.mitre.org/data/definitions/16.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Open the production environment's configuration file and compare the value with the recommended one: debug mode off, restricted origins and no test values.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | .NET |
| Languages | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Security Misconfiguration |
