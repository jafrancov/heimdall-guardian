# NET-CONF-003: CORS open with credentials (.NET)

[Back to the rules catalog](index.md)

## What it detects

CORS allows any origin together with credentials: any website can make authenticated requests on behalf of the user.

## How to fix it

Replace AllowAnyOrigin() with WithOrigins() listing the system's real domains.

## Why it matters

This rule maps to [CWE-942](https://cwe.mitre.org/data/definitions/942.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Check the CORS configuration: origins should be a specific list; an open origin with credentials lets other sites read session data.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Security Misconfiguration |
