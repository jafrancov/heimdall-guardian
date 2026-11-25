# SWIFT-NET-001: Unencrypted http:// address in the code (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Unencrypted http:// address: the application's traffic travels in cleartext and anyone on the same network can read or modify it. iOS blocks this traffic by default (App Transport Security), so it usually also forces an exception to be opened in Info.plist.

## How to fix it

Use https:// for all service addresses. For local development, localhost and 127.0.0.1 are allowed; if a test environment has no certificate, fix it there instead of accepting http in the released version.

## Why it matters

This rule maps to [CWE-319](https://cwe.mitre.org/data/definitions/319.html) and to the OWASP Top 10:2025 category A04:2025 Cryptographic Failures.

## How to verify it

Check the server and client configuration: communication should use TLS. Confirm that there are no `http://` addresses to services that handle data.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-319](https://cwe.mitre.org/data/definitions/319.html) |
| OWASP | A04:2025 Cryptographic Failures |
