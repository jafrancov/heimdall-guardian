# NODE-CRY-001: Weak cryptography or predictable randomness (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Weak cryptography: MD5 or SHA-1 hashing applied to passwords, Math.random() used to generate tokens or passwords (not cryptographically secure), createCipher without an initialization vector, or encryption in ECB mode or with DES.

## How to fix it

For passwords, use bcrypt, scrypt (crypto.scrypt) or argon2. For tokens, use crypto.randomBytes or crypto.randomUUID. For encryption, use createCipheriv with AES-256-GCM and a random IV per message; never ECB.

## Why it matters

This rule maps to [CWE-327](https://cwe.mitre.org/data/definitions/327.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Identify what the algorithm is used for. If it protects passwords or data, replace it with a current one (Argon2, bcrypt or scrypt; AES-GCM). MD5 or SHA-1 are only fine for checksums with no security value.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Cryptographic Failures |
