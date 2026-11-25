# NODE-CONF-001: CORS open to any origin with credentials (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Permissive CORS with credentials: the server accepts requests carrying cookies or authentication headers from any site (origin '*', true, or the reflected request origin). A third-party page can act on behalf of the authenticated user.

## How to fix it

Declare a closed list of allowed origins (origin: ['https://app.example.com']) or a function that checks against one, and enable credentials only for them. Never reflect the request origin without validating it.

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
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Security Misconfiguration |
