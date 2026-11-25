# PHP-CONF-002: Hard-coded production/debug flag (PHP)

[Back to the rules catalog](index.md)

## What it detects

The production or debug flag is hard-coded in PHP (PRODUCTION = false, DEBUG = true). Whatever the server's php.ini says, code that shows errors or turns on debug behaviour from this flag does it in production too, and nobody notices until the file is changed by hand on each deployment.

## How to fix it

Read the environment from the server configuration (an environment variable or a file outside the repository) and default to production behaviour when it is missing. Do not commit a debug value that changes what the application shows to visitors.

## Why it matters

This rule maps to [CWE-489](https://cwe.mitre.org/data/definitions/489.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Confirm in the production environment that debug mode is off and that no development console is reachable.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | CONFIGURATION |
| Stack | PHP and Laravel |
| Languages | `regex` |
| CWE | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) |
| OWASP | A02:2025 Security Misconfiguration |
