# NODE-XSS-001: Reflected XSS: request data in the response without escaping (Node.js)

[Back to the rules catalog](index.md)

## What it detects

Request data is sent in the response (res.send, res.write, res.end) without escaping. Express answers strings with text/html, so the browser runs the injected HTML or script (reflected XSS).

## How to fix it

Escape the output with an HTML encoding function (escape-html, he.encode) or return JSON with res.json. For formatted HTML, use a template engine that escapes by default (EJS &lt;%= %&gt;, Handlebars {{ }}, Pug =) or sanitize with DOMPurify or sanitize-html.

## Why it matters

This rule maps to [CWE-79](https://cwe.mitre.org/data/definitions/79.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Find where the data is printed on the page and confirm that it is escaped for its context (HTML, attribute or script). In testing, try a text like `&lt;b&gt;x&lt;/b&gt;`.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Injection |
