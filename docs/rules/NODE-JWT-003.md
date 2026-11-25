# NODE-JWT-003: JWT decoded without verifying the signature (Node.js)

[Back to the rules catalog](index.md)

## What it detects

A JWT is decoded without verifying its signature in the same function. decode only reads the content: anyone can forge a token that says whatever they want.

## How to fix it

Use jwt.verify (or jwtService.verify) to decide whether the user is authenticated and to read their data; reserve decode for information not used in security decisions.

## Why it matters

This rule maps to [CWE-345](https://cwe.mitre.org/data/definitions/345.html) and to the OWASP Top 10:2025 category A07:2025 Authentication Failures.

## How to verify it

Check whether the data is accepted without verifying its origin or integrity. A signature or an authentication code should be verified before using it.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-345](https://cwe.mitre.org/data/definitions/345.html) |
| OWASP | A07:2025 Authentication Failures |
