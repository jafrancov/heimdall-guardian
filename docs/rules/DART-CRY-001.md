# DART-CRY-001: Weak cryptography or predictable randomness (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

Weak cryptography: MD5 or SHA-1 applied to passwords, Random() (non-cryptographic) used to generate tokens, passwords, codes or nonces, AES encryption in ECB mode, or a fixed initialization vector. Passwords can be brute-forced, random values can be predicted, and a repeated IV reveals patterns in the ciphertext.

## How to fix it

For passwords, use a slow salted algorithm (argon2, bcrypt or scrypt) on the server. For tokens, codes and nonces, use Random.secure(). For encryption, use AES in GCM mode (or CBC with HMAC) with a new random IV per message (IV.fromSecureRandom(16)); never ECB or fixed IVs.

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
| Stack | Dart and Flutter |
| Languages | `dart` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Cryptographic Failures |
