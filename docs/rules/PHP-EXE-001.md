# PHP-EXE-001: Command execution with variable input (PHP)

[Back to the rules catalog](index.md)

## What it detects

Execution of code or system commands with a variable argument. If the value comes from the user, it allows arbitrary commands to run on the server.

## How to fix it

Remove eval/exec/system/shell_exec/passthru on variable data. If the command is essential, use an allowlist of values and escapeshellarg() on each argument.

## Why it matters

This rule maps to [CWE-78](https://cwe.mitre.org/data/definitions/78.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Check whether the command text is built from user data. Use an argument list with no shell and with allowed values.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| OWASP | A05:2025 Injection |
