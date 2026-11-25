# DJ-CONF-001: DEBUG turned on in settings

[Back to the rules catalog](index.md)

## What it detects

DEBUG = True in a settings file that is not for development. In production it exposes stack traces, paths, SQL queries and part of the configuration to any visitor.

## How to fix it

Set DEBUG = False by default and turn it on only from an environment variable on development machines.

## Why it matters

This rule maps to [CWE-489](https://cwe.mitre.org/data/definitions/489.html) and to the OWASP Top 10:2025 category A02:2025 Security Misconfiguration.

## How to verify it

Confirm in the production environment that debug mode is off and that no development console is reachable.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | CONFIGURATION |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) |
| OWASP | A02:2025 Security Misconfiguration |
