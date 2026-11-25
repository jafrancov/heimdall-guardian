# NET-SQL-001: Dynamic SQL in a direct query (.NET)

[Back to the rules catalog](index.md)

## What it detects

SQL query built with string concatenation or interpolation. If any value comes from the user, it allows SQL injection.

## How to fix it

Use parameters (SqlParameter, FromSqlInterpolated, ExecuteSqlInterpolated) or LINQ. Never concatenate values into the query text.

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
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
