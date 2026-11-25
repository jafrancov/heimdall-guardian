# KT-STO-001: Token or password in SharedPreferences or DataStore (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

Sensitive data saved in unencrypted SharedPreferences or DataStore: both write files that can be read by anyone with the device rooted, from a backup (adb backup, Auto Backup), or by another application with access to that storage.

## How to fix it

Store tokens, passwords, PINs and keys encrypted with an Android Keystore key: EncryptedSharedPreferences, or DataStore encrypted with Tink. Keep only what is essential on the device, with a short lifetime, and exclude those files from backup.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Cryptographic Failures |
