# DART-CONF-001: Insecure configuration in AndroidManifest.xml or Info.plist

[Back to the rules catalog](index.md)

## What it detects

Insecure native configuration of the mobile app (Android or iOS): cleartext http traffic allowed, debuggable application, or backup enabled. Each one widens what an attacker with network or device access can obtain.

## How to fix it

In AndroidManifest.xml, use usesCleartextTraffic="false" (or define a network_security_config with only the necessary domains), debuggable="false" and allowBackup="false" in the released version. In Info.plist, remove NSAllowsArbitraryLoads and declare exceptions per domain only. Local testing can go in android/app/src/debug.

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
| Stack | Dart and Flutter |
| Languages | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Security Misconfiguration |
