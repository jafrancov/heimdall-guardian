# NET-CAND-005: Redirect to a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

The user is redirected to a destination that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Redirect only to relative paths or to hosts on an allow list.

## Why it matters

This rule maps to [CWE-601](https://cwe.mitre.org/data/definitions/601.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check whether the redirect destination comes from request data. It should be compared with a list of allowed destinations or limited to internal paths.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-601](https://cwe.mitre.org/data/definitions/601.html) |
| OWASP | A01:2025 Broken Access Control |
