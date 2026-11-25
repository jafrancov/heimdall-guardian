# DJ-XSS-001: Unescaped HTML: mark_safe with variable data

[Back to the rules catalog](index.md)

## What it detects

mark_safe() on a variable value turns off HTML escaping. If the value contains user data, it allows script injection (XSS).

## How to fix it

Use format_html(), which escapes each argument, or let the template escape the value.

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
| Languages | `python` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Injection |
