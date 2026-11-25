# PHP-CRY-001: Passwords hashed with md5/sha1 (PHP)

[Back to the rules catalog](index.md)

## What it detects

Password protected with md5() or sha1(). They are fast, unsalted functions: passwords can be recovered in minutes if the database leaks.

## How to fix it

Use password_hash() when storing and password_verify() when checking, and migrate existing passwords at the next login.

## Why it matters

This rule maps to [CWE-916](https://cwe.mitre.org/data/definitions/916.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Check how passwords are stored: they should use a slow algorithm with a salt (Argon2, bcrypt or scrypt), never MD5, SHA-1 or plain SHA-256.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-916](https://cwe.mitre.org/data/definitions/916.html) |
| OWASP | A04:2025 Cryptographic Failures |
