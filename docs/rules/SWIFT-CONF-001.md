# SWIFT-CONF-001: Insecure configuration in Info.plist or .entitlements (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Insecure native configuration in the iOS app: App Transport Security disabled (allows cleartext http traffic, globally or per domain) or entitlements with get-task-allow, which allow attaching a debugger to the application. Each one widens what an attacker with network or device access can obtain.

## How to fix it

In Info.plist, remove NSAllowsArbitraryLoads, NSAllowsArbitraryLoadsInWebContent and NSExceptionAllowsInsecureHTTPLoads, and declare exceptions per domain only and, if possible, for testing only. In .entitlements files of the released version, get-task-allow must be false or omitted; Xcode adds it only to debug builds.

## Why it matters

This rule maps to [CWE-16](https://cwe.mitre.org/data/definitions/16.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Open the production environment's configuration file and compare the value with the recommended one: debug mode off, restricted origins and no test values.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | CONFIGURATION |
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Security Misconfiguration |
