# NODE-SQL-001: SQL injection with request data (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data (req.query, req.body, req.params, headers or NestJS parameters) reaches an SQL query built by concatenation or a template string: this allows SQL injection.

## How to fix it

Use parameterized queries: db.query('SELECT ... WHERE id = $1', [id]) or db.query('... WHERE id = ?', [id]); with Prisma, $queryRaw as a tagged template; with Sequelize, replacements or bind; with Knex, bindings or the query builder. Never interpolate values into the query text.

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
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Injection |
