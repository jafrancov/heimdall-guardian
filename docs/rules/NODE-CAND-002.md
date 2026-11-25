# NODE-CAND-002: Command built from a variable (to review)

[Back to the rules catalog](index.md)

## What it detects

> Candidate: only reviewed by the local AI, never reported on its own

A system command is run with a value that is not a constant. It is only a point to review: the local AI checks whether untrusted input reaches it.

## How to fix it

Avoid the shell; pass the program and its arguments as a list and validate every value against an allow list.

## Why it matters

This rule maps to [CWE-78](https://cwe.mitre.org/data/definitions/78.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the command text is built from user data. Use an argument list with no shell and with allowed values.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Injection |
