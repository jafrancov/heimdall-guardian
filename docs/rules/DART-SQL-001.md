# DART-SQL-001: SQL query built from text (sqflite/drift, Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

SQL injection: the query is built with interpolation ($variable or ${expression}) or text concatenation instead of bound arguments. A value such as `' OR 1=1 --` alters the query and can read or delete the application's local database.

## How to fix it

Use ? placeholders with the argument list (rawQuery('... WHERE id = ?', [id])), the where/whereArgs parameters of query, update and delete, or drift's typed queries. In drift, use Variable&lt;T&gt; inside customSelect. Never interpolate values into the SQL.

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
| Stack | Dart and Flutter |
| Languages | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
