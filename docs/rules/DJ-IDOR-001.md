# DJ-IDOR-001: Possible access to other people's objects (IDOR)

[Back to the rules catalog](index.md)

## What it detects

An object is fetched only by its identifier, taken from the URL, without filtering by the user or organization of the requester. Without other validation, a user can read or modify other people's records by changing the identifier (IDOR).

## How to fix it

Also filter by the owner, for example get_object_or_404(Model, pk=pk, user=request.user), or check the permission on the object before using it.

## Why it matters

This rule maps to [CWE-639](https://cwe.mitre.org/data/definitions/639.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Test with two different accounts in a test environment: account A asks for the identifier of one of B's records and should get 403 or 404.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | ACCESS CONTROL |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) |
| OWASP | A01:2025 Broken Access Control |
