# KT-CAND-001: SQL built from a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

A SQL query is built by joining or interpolating a variable. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Use parameterized queries and never put values into the query text.

## Why it matters

This rule maps to [CWE-89](https://cwe.mitre.org/data/definitions/89.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the query is built by joining text with user data. It should use bound parameters; confirm that no data reaches the query as text.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
