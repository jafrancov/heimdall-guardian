# KT-SQL-001: SQL query built from text (SQLite or Room, Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

SQL injection: the SQLite or Room query is built with a string template ($value, ${value}) or concatenation instead of bound arguments. A value such as `' OR 1=1 --` alters the query and can read or delete the application's local database; if the query is exposed through a ContentProvider, it can also affect other applications.

## How to fix it

Use ? placeholders with the argument list (db.rawQuery("... WHERE id = ?", arrayOf(id)), or SimpleSQLiteQuery("... ?", arrayOf(id)) in Room) or, better, @Query queries with :name parameters. Never interpolate or concatenate values into the SQL; variable table or column names must be validated against a fixed list.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
