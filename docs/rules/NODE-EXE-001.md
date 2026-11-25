# NODE-EXE-001: Command injection with request data (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data reaches a system command (child_process.exec, execSync, spawn or execFile with a shell, shelljs.exec): this allows arbitrary command execution on the server.

## How to fix it

Avoid the command shell: use execFile or spawn without shell:true and pass the arguments as an array, validated against an allowlist. If building a command is unavoidable, escape each argument with shell-quote.

## Why it matters

This rule maps to [CWE-78](https://cwe.mitre.org/data/definitions/78.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the command text is built from user data. Use an argument list with no shell and with allowed values.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | HIGH |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Injection |
