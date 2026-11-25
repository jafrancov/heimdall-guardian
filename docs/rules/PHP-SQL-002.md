# PHP-SQL-002: SQL injection through a function parameter (PHP)

[Back to the rules catalog](index.md)

## What it detects

A parameter of this function or method reaches the SQL text without a cast or escaping. Whoever calls it with request data (often a controller) opens SQL injection.

## How to fix it

Use prepared statements with bound parameters ($stmt = $db-&gt;prepare(...); $stmt-&gt;bind_param(...)). If you must build the text, cast numbers with (int) and escape strings with the driver's function.

## Why it matters

This rule maps to [CWE-89](https://cwe.mitre.org/data/definitions/89.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the query is built by joining text with user data. It should use bound parameters; confirm that no data reaches the query as text.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
