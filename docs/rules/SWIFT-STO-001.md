# SWIFT-STO-001: Token or password in UserDefaults or @AppStorage (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Sensitive data saved in UserDefaults or @AppStorage: it is written to an unencrypted plist file that is included in device backups and is easily read on a jailbroken device or from an extracted backup.

## How to fix it

Store tokens, passwords, PINs and keys in the Keychain (SecItemAdd, with kSecAttrAccessibleWhenUnlockedThisDeviceOnly or kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly), not in UserDefaults or @AppStorage. Keep only what is essential on the device, with a short lifetime.

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
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Cryptographic Failures |
