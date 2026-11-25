# DART-TLS-001: TLS certificate validation disabled (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

Certificate validation disabled: the callback that decides what to do with an invalid certificate always answers yes. Anyone on the network (a public Wi-Fi, for example) can impersonate the server and read or modify the traffic.

## How to fix it

Remove the callback (badCertificateCallback, onBadCertificate or validateCertificate returning true) and let the platform validate the chain. If you need to trust your own CA, add it with SecurityContext.setTrustedCertificatesBytes or pin the certificate by comparing its fingerprint; never accept everything.

## Why it matters

This rule maps to [CWE-295](https://cwe.mitre.org/data/definitions/295.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Check whether certificate validation is turned off. The chain of trust and the server name should always be validated.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | Dart and Flutter |
| Languages | `dart` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Cryptographic Failures |
