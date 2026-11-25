# NODE-DES-001: Insecure deserialization (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Insecure deserialization: node-serialize.unserialize runs functions embedded in the text, js-yaml with the full schema builds arbitrary objects and functions, and evaluating JSON with eval runs any code it contains.

## How to fix it

Do not use node-serialize: exchange data as JSON with JSON.parse. With js-yaml, use yaml.load with the default schema of version 4 or DEFAULT_SCHEMA/JSON_SCHEMA, never DEFAULT_FULL_SCHEMA. Do not evaluate JSON with eval.

## Why it matters

This rule maps to [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and to the OWASP Top 10:2025 category A08:2025 Software or Data Integrity Failures.

## How to verify it

Identify where the deserialized data comes from. If it is not fully trusted, use a simple data format (JSON) with schema validation.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Software or Data Integrity Failures |
