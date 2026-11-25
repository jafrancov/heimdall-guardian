# DART-STO-001: Token or password in unencrypted storage (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

Sensitive data saved in unencrypted storage: SharedPreferences and GetStorage write plain-text files that can be read by anyone with the device rooted or jailbroken, or from a backup.

## How to fix it

Store tokens, passwords, PINs and keys with flutter_secure_storage (Keychain on iOS, Keystore on Android), not in SharedPreferences or GetStorage. Keep only what is essential on the device, with a short lifetime.

## Why it matters

This rule maps to [CWE-312](https://cwe.mitre.org/data/definitions/312.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Check where the data is stored: on the device, SharedPreferences and GetStorage are readable files. Sensitive data should go in the keychain (flutter_secure_storage).

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Dart and Flutter |
| Languages | `dart` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Cryptographic Failures |
