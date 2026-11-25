# SWIFT-TLS-001: TLS certificate validation disabled (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Certificate validation disabled: the URLSession delegate accepts any server certificate without evaluating it, or an evaluator that validates nothing is used. Anyone on the network (a public Wi-Fi, for example) can impersonate the server and read or modify the traffic.

## How to fix it

Remove the didReceive challenge method so the system validates the chain, or evaluate serverTrust with SecTrustEvaluateWithError before answering .useCredential. If you need to trust your own CA or pin the certificate, compare the public key or fingerprint of the received certificate with the expected one and cancel the challenge if they do not match. In Alamofire, use PinnedCertificatesTrustEvaluator or DefaultTrustEvaluator instead of DisabledTrustEvaluator.

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
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-295](https://cwe.mitre.org/data/definitions/295.html) |
| OWASP | A04:2025 Cryptographic Failures |
