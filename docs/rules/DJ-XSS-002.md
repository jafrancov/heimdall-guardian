# DJ-XSS-002: Unescaped HTML in a template (\|safe, autoescape off)

[Back to the rules catalog](index.md)

## What it detects

The template turns off automatic HTML escaping (safe filter or autoescape off). If the value contains user data, it allows script injection (XSS).

## How to fix it

Remove the safe filter or the autoescape off block. If rich HTML is needed, sanitize it on the server first with an allowlist of tags.

## Why it matters

This rule maps to [CWE-79](https://cwe.mitre.org/data/definitions/79.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Find where the data is printed on the page and confirm that it is escaped for its context (HTML, attribute or script). In testing, try a text like `&lt;b&gt;x&lt;/b&gt;`.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Python and Django |
| Languages | `regex` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Injection |
