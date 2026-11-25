# NODE-SSRF-001: Server-side request to a request-controlled URL (SSRF, Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data is used as the address of a server-side HTTP request (axios, fetch, got, request, http.get, needle...): this lets an attacker query internal services or cloud metadata (SSRF).

## How to fix it

Do not accept full URLs from the user. Choose the destination from an allowlist of hosts or keys, validate the scheme (https only) and block private, loopback and metadata addresses (169.254.169.254) after resolving the name.

## Why it matters

This rule maps to [CWE-918](https://cwe.mitre.org/data/definitions/918.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check whether the address the server fetches comes from the request. It should be validated against a list of allowed destinations, blocking internal addresses.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) |
| OWASP | A01:2025 Broken Access Control |
