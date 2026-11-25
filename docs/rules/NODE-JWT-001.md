# NODE-JWT-001: JWT with the none algorithm or without expiration validation (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Weakened JWT verification or issuance: the none algorithm (no signature) is accepted or the token expiration is ignored.

## How to fix it

Set a closed list of signing algorithms (for example algorithms: ['HS256'] or ['RS256']), never include none, and do not use ignoreExpiration: true. If an expired token must be renewed, do it with a refresh token.

## Why it matters

This rule maps to [CWE-347](https://cwe.mitre.org/data/definitions/347.html) and to the OWASP Top 10:2025 category A07:2025 Authentication Failures.

## How to verify it

Check how the token is decoded: the signature should be verified with the right key and a fixed algorithm, never the one the token itself indicates.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-347](https://cwe.mitre.org/data/definitions/347.html) |
| OWASP | A07:2025 Authentication Failures |
