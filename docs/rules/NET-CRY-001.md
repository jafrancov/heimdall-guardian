# NET-CRY-001: Weak cryptography (.NET)

[Back to the rules catalog](index.md)

## What it detects

Weak cryptographic algorithm (MD5, SHA-1, DES or 3DES). It is not suitable for protecting passwords or sensitive data.

## How to fix it

For passwords, use ASP.NET Identity's PasswordHasher or Rfc2898DeriveBytes (PBKDF2). For encryption, use AES; for integrity, SHA-256 or higher.

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
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Cryptographic Failures |
