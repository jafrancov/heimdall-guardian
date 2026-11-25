# KT-CAND-004: Request to a URL from a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

An HTTP request goes to a URL that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Validate the host against an allow list and block private and internal addresses.

## Why it matters

This rule maps to [CWE-918](https://cwe.mitre.org/data/definitions/918.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check whether the address the server fetches comes from the request. It should be validated against a list of allowed destinations, blocking internal addresses.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) |
| OWASP | A01:2025 Broken Access Control |
