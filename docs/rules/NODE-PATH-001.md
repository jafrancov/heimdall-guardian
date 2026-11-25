# NODE-PATH-001: File access with a request-controlled path (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data forms a file path (fs.readFile, createReadStream, writeFile, unlink, res.sendFile, res.download...) without being reduced to a file name: it allows reading, writing or deleting files outside the intended folder (path traversal).

## How to fix it

Reduce the input to a file name with path.basename() or an allowlist, resolve it against a fixed base folder with path.resolve and check that the result is still inside it; in Express, use res.sendFile(name, { root: folder }).

## Why it matters

This rule maps to [CWE-22](https://cwe.mitre.org/data/definitions/22.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Follow the parameter to the function that opens the file and confirm that the path is normalized and limited to a base directory. Try `../` in a test environment.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) |
| OWASP | A01:2025 Broken Access Control |
