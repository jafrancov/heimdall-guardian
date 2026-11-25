# NODE-NOSQL-001: NoSQL injection with request data (Node.js)

[Back to the rules catalog](index.md)

## What it detects

A request value is used as a MongoDB or Mongoose filter without being converted to a string: a JSON body such as {"$ne": null} changes the meaning of the query (NoSQL injection). The $where operator with request data also allows running JavaScript in the database.

## How to fix it

Convert each filter value to the expected type before querying (String(value), Number(value), new ObjectId(value)), validate the body with a schema (Joi, Zod, class-validator), or strip operators with express-mongo-sanitize. Do not use $where with user data.

## Why it matters

This rule maps to [CWE-943](https://cwe.mitre.org/data/definitions/943.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the query filter is built from objects sent by the user. Validate that each value is of the expected type (text, number) before using it.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-943](https://cwe.mitre.org/data/definitions/943.html) |
| OWASP | A05:2025 Injection |
