# PHP-MAS-001: Mass assignment (Laravel)

[Back to the rules catalog](index.md)

## What it detects

Mass assignment: every request field is saved, or the model protects none. A user can modify fields they should not, such as the role or the record's owner.

## How to fix it

Use $request-&gt;validated() or $request-&gt;only([...]) and declare $fillable on the model with the allowed fields.

## Why it matters

This rule maps to [CWE-915](https://cwe.mitre.org/data/definitions/915.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check which fields the model accepts from the request. There should be an explicit list of allowed fields; confirm that, for example, a role cannot be sent.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-915](https://cwe.mitre.org/data/definitions/915.html) |
| OWASP | A06:2025 Insecure Design |
