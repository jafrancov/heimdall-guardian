# SWIFT-CRY-001: Weak cryptography or fixed initialization vector (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Weak cryptography: MD5 or SHA-1 applied to passwords, ECB mode encryption, a fixed initialization vector (IV), or a predictable random generator for tokens, codes or passwords. Passwords can be brute-forced, ECB reveals patterns in the ciphertext, and a repeated IV defeats the protection of CBC or GCM mode.

## How to fix it

For passwords, use a slow salted algorithm (Argon2, bcrypt or PBKDF2 with CCKeyDerivationPBKDF) and, preferably, verify them on the server. For encryption, use CryptoKit's AES.GCM, which generates a new random nonce per message; never ECB or literal IVs. For tokens and codes, use SecRandomCopyBytes or SystemRandomNumberGenerator, not rand() or random().

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
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Cryptographic Failures |
