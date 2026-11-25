# SWIFT-DES-001: Deserialization without class restriction using NSKeyedUnarchiver (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Insecure deserialization with NSKeyedUnarchiver: unarchiveObject(with:) does not restrict the classes it reconstructs, and requiresSecureCoding set to false explicitly allows it. Tampered data (a shared file, a backup, the clipboard) can instantiate unexpected classes and alter the application's behavior.

## How to fix it

Use NSKeyedUnarchiver.unarchivedObject(ofClass:from:) or unarchivedObject(ofClasses:from:) with the minimum list of allowed classes, and keep requiresSecureCoding set to true. For your own data, prefer Codable with JSONDecoder.

## Why it matters

This rule maps to [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and to the OWASP Top 10:2025 category A08:2025 Software or Data Integrity Failures.

## How to verify it

Identify where the deserialized data comes from. If it is not fully trusted, use a simple data format (JSON) with schema validation.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | SAST |
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Software or Data Integrity Failures |
