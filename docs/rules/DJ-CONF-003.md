# DJ-CONF-003: ALLOWED_HOSTS or CORS open to any origin

[Back to the rules catalog](index.md)

## What it detects

Configuration open to any origin: ALLOWED_HOSTS with a wildcard or CORS allowed for all origins.

## How to fix it

List the system's real domains in ALLOWED_HOSTS and in CORS_ALLOWED_ORIGINS.

## Why it matters

This rule maps to [CWE-942](https://cwe.mitre.org/data/definitions/942.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Check the CORS configuration: origins should be a specific list; an open origin with credentials lets other sites read session data.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Security Misconfiguration |
