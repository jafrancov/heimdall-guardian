# KT-CRY-001: Weak cryptographic algorithm, fixed IV or insecure randomness (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

Weak cryptography: an MD5 or SHA-1 digest, AES encryption in ECB mode (or plain "AES", which on Android is equivalent to ECB), DES, 3DES, RC4 or Blowfish, a fixed initialization vector (IV), or a non-cryptographic generator (Random) for a token, password, code or salt. Data protected this way can be decrypted, forged or predicted.

## How to fix it

Encrypt with AES/GCM/NoPadding using an Android Keystore key and a new random IV for every operation (store it alongside the ciphertext). Hash with SHA-256 or stronger, and store passwords with a slow algorithm (Argon2, bcrypt, PBKDF2 with many iterations). For tokens and codes, use SecureRandom.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Cryptographic Failures |
