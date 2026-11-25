# NODE-JWT-002: Hard-coded JWT secret (Node.js)

[Back to the rules catalog](index.md)

## What it detects

The secret used to sign or verify JWT tokens is written in the code. Anyone who can read the repository can issue valid tokens.

## How to fix it

Read the secret from an environment variable or a secrets manager (process.env.JWT_SECRET), use a long random value, and rotate any that has been in the repository. To sign with an asymmetric key, load the private key from a file outside the code.

## Why it matters

This rule maps to [CWE-798](https://cwe.mitre.org/data/definitions/798.html) and to the OWASP Top 10:2025 category A07:2025 Authentication Failures.

## How to verify it

Look for the value in the version history and confirm whether it is still valid. If it is, rotate it right away and move it to a secrets manager.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Authentication Failures |
