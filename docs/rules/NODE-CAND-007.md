# NODE-CAND-007: XML parsed from a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

An XML document is parsed from a value that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Disable DTDs and external entities in the XML parser, or use a parser configured to refuse them.

## Why it matters

This rule maps to [CWE-611](https://cwe.mitre.org/data/definitions/611.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Check the XML parser: external entities and document type definitions should be turned off.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-611](https://cwe.mitre.org/data/definitions/611.html) |
| OWASP | A02:2025 Security Misconfiguration |
