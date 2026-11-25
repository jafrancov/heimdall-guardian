# KT-TLS-001: TLS certificate validation disabled (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

Secure connection validation is disabled: a TrustManager that accepts any certificate, a HostnameVerifier that always returns true, ALLOW_ALL_HOSTNAME_VERIFIER, or a WebView that continues after a certificate error (handler.proceed()). Anyone on the same network can intercept and modify the traffic with a fake certificate.

## How to fix it

Remove the custom TrustManager and HostnameVerifier and use the system ones. If the server uses its own authority, declare it in network_security_config.xml or pin the certificate with OkHttp's CertificatePinner. In onReceivedSslError, call handler.cancel() and show the error to the user.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Cryptographic Failures |
