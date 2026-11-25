# KT-STO-002: File or preferences with permissions for other applications (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

A file or preference is created with MODE_WORLD_READABLE or MODE_WORLD_WRITEABLE: any other application on the device can read or modify it. Modern Android throws an exception, but on older versions the file is left open.

## How to fix it

Use MODE_PRIVATE. To share a file with another application, expose it through a FileProvider with temporary URI permissions, not with global file permissions.

## Why it matters

This rule maps to [CWE-732](https://cwe.mitre.org/data/definitions/732.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check the file or resource permissions: only whoever needs to should be able to read or write it.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-732](https://cwe.mitre.org/data/definitions/732.html) |
| OWASP | A01:2025 Broken Access Control |
