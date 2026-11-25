# PHP-XSS-001: XSS: request data output without escaping (PHP)

[Back to the rules catalog](index.md)

## What it detects

Request data is written to the page without escaping: it allows injecting scripts into other users' browsers (XSS).

## How to fix it

Escape with htmlspecialchars($value, ENT_QUOTES, 'UTF-8') when writing into HTML, or use the template engine's automatic escaping.

## Why it matters

This rule maps to [CWE-79](https://cwe.mitre.org/data/definitions/79.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Find where the data is printed on the page and confirm that it is escaped for its context (HTML, attribute or script). In testing, try a text like `&lt;b&gt;x&lt;/b&gt;`.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Injection |
