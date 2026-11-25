# SWIFT-SQL-001: SQL query built from text (SQLite, GRDB or FMDB, Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

SQL injection: the query is built with interpolation (\(value)) or text concatenation instead of bound arguments. A value such as `' OR 1=1 --` alters the query and can read or delete the application's local database.

## How to fix it

Use ? or :name placeholders with the argument list (db.execute(sql: "... WHERE id = ?", arguments: [id]) in GRDB, executeQuery("... ?", values: [id]) in FMDB, sqlite3_bind_* with sqlite3_prepare_v2). In GRDB, interpolation is safe only with literal SQL (execute(literal:) or the typed query API). Never interpolate values into the SQL.

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
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
