# KT-CONF-001: Exported component without permission or http traffic allowed (AndroidManifest.xml)

[Back to the rules catalog](index.md)

## What it detects

Exported Android component without permission: an activity, service, receiver or provider with android:exported="true" and no android:permission can be invoked by any installed application; a provider with grantUriPermissions="true" also lets access to its data be granted by URI. Allowed cleartext http traffic in network_security_config.xml is also flagged.

## How to fix it

Declare android:exported="false" unless the component must receive calls from other applications; in that case require a signature-level android:permission, validate every Intent received and do not trust its data. File providers must be FileProvider with exported="false" and grantUriPermissions="true". In network_security_config.xml, allow http only for specific development domains and never in base-config.

## Why it matters

This rule maps to [CWE-926](https://cwe.mitre.org/data/definitions/926.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Open AndroidManifest.xml and check each component with android:exported="true": does it need to receive calls from other apps? If not, set it to false; if it does, require a signature permission and test with `adb shell am start` that it rejects invalid data.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | CONFIGURATION |
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-926](https://cwe.mitre.org/data/definitions/926.html) |
| OWASP | A02:2025 Security Misconfiguration |
