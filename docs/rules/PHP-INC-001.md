# PHP-INC-001: File inclusion with a variable path (PHP)

[Back to the rules catalog](index.md)

## What it detects

include/require with a path that depends on a variable. If the value comes from the user, it allows including arbitrary files and running code.

## How to fix it

Include fixed paths only. If the page depends on a parameter, resolve it against an allowlist of permitted files.

## Why it matters

This rule maps to [CWE-98](https://cwe.mitre.org/data/definitions/98.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the path of the included file depends on external data. It should be chosen from a fixed list, never built from the input.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-98](https://cwe.mitre.org/data/definitions/98.html) |
| OWASP | A05:2025 Injection |
