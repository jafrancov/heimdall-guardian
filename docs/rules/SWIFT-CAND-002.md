# SWIFT-CAND-002: File path from a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

A file is opened with a path that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Resolve the path against a fixed base folder and reject any result that falls outside it.

## Why it matters

This rule maps to [CWE-22](https://cwe.mitre.org/data/definitions/22.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Follow the parameter to the function that opens the file and confirm that the path is normalized and limited to a base directory. Try `../` in a test environment.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) |
| OWASP | A01:2025 Broken Access Control |
