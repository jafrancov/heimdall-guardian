# SWIFT-KEY-001: Keychain item with «always» accessibility (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Keychain item with weak accessibility: kSecAttrAccessibleAlways (and its ThisDeviceOnly variant) leaves the data available even when the device is locked and freshly booted, and Apple has deprecated it. An attacker holding the device can read it without unlocking it.

## How to fix it

Use kSecAttrAccessibleWhenUnlockedThisDeviceOnly for data needed only while the app is in use, or kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly if a background task must read it. For highly sensitive data, add an access control with biometrics (SecAccessControlCreateWithFlags).

## Why it matters

This rule maps to [CWE-311](https://cwe.mitre.org/data/definitions/311.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Confirm with the infrastructure team whether the data travels or is stored unencrypted and which encryption mechanism is used.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | SAST |
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-311](https://cwe.mitre.org/data/definitions/311.html) |
| OWASP | A04:2025 Cryptographic Failures |
