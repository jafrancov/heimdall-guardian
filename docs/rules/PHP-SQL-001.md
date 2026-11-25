# PHP-SQL-001: SQL injection with request data (PHP)

[Back to the rules catalog](index.md)

## What it detects

Request data ($_GET, $_POST, $_REQUEST or $_COOKIE) reaches a SQL query without parameterization: it allows SQL injection.

## How to fix it

Use prepared statements (PDO::prepare or mysqli_prepare with bind_param). Never concatenate request data into the query.

## Why it matters

This rule maps to [CWE-89](https://cwe.mitre.org/data/definitions/89.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the query is built by joining text with user data. It should use bound parameters; confirm that no data reaches the query as text.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | HIGH |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
