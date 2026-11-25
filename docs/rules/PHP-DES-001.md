# PHP-DES-001: Deserialization of request data (PHP)

[Back to the rules catalog](index.md)

## What it detects

unserialize() on request data: it allows arbitrary objects to be instantiated and can lead to remote code execution.

## How to fix it

Exchange data with json_decode(). If unserialize() is essential, use ['allowed_classes' =&gt; false] and sign the content.

## Why it matters

This rule maps to [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and to the OWASP Top 10:2025 category A08:2025 Software or Data Integrity Failures.

## How to verify it

Identify where the deserialized data comes from. If it is not fully trusted, use a simple data format (JSON) with schema validation.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Software or Data Integrity Failures |
