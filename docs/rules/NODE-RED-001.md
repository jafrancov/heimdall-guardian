# NODE-RED-001: Open redirect with request data (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data decides where the server redirects (res.redirect, res.location). A crafted link can send the user to a fake site that looks like the application (open redirect).

## How to fix it

Redirect only to your own relative paths: check that the destination starts with a single slash (not // or a scheme) or compare it against an allowlist of destinations and hosts.

## Why it matters

This rule maps to [CWE-601](https://cwe.mitre.org/data/definitions/601.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Check whether the redirect destination comes from request data. It should be compared with a list of allowed destinations or limited to internal paths.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-601](https://cwe.mitre.org/data/definitions/601.html) |
| OWASP | A01:2025 Broken Access Control |
