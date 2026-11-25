# NODE-EXE-002: Code execution with request data (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data is evaluated as JavaScript code (eval, new Function, vm.runIn*Context, new vm.Script, or setTimeout/setInterval with a string): this allows arbitrary code execution on the server.

## How to fix it

Remove eval, new Function and vm on user data. For expressions or data formats, use a dedicated parser (JSON.parse, an expression library that does not execute code) and, for variable logic, an allowlist of operations.

## Why it matters

This rule maps to [CWE-95](https://cwe.mitre.org/data/definitions/95.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Look for any external data reaching `eval` or an equivalent. Replace it with a closed list of operations or a safe parser for the data.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | HIGH |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-95](https://cwe.mitre.org/data/definitions/95.html) |
| OWASP | A05:2025 Injection |
