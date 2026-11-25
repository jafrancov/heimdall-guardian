# PHP-CAND-006: Deserialization of a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

Data is deserialized from a value that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Never deserialize untrusted data with a format that can build arbitrary objects; use a data-only format such as JSON with a fixed schema, or restrict the allowed types.

## Why it matters

This rule maps to [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and to the OWASP Top 10:2025 category A08:2025 Software or Data Integrity Failures.

## How to verify it

Identify where the deserialized data comes from. If it is not fully trusted, use a simple data format (JSON) with schema validation.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Software or Data Integrity Failures |
