# NODE-XSS-002: Dynamic HTML inserted into the DOM without sanitizing (JavaScript)

[Back to the rules catalog](index.md)

## What it detects

Dynamic HTML is inserted into the page (innerHTML, outerHTML, insertAdjacentHTML, document.write, dangerouslySetInnerHTML or jQuery .html). If the value includes unsanitized user data, it allows script execution (DOM-based XSS).

## How to fix it

Assign text with textContent or create nodes with createElement. If HTML is needed, sanitize it first with DOMPurify.sanitize(value). In React, avoid dangerouslySetInnerHTML or sanitize the value.

## Why it matters

This rule maps to [CWE-79](https://cwe.mitre.org/data/definitions/79.html) and to the OWASP Top 10:2025 category A05:2025 Injection.

## How to verify it

Find where the data is printed on the page and confirm that it is escaped for its context (HTML, attribute or script). In testing, try a text like `&lt;b&gt;x&lt;/b&gt;`.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Node.js and TypeScript |
| Languages | `javascript`, `typescript` |
| CWE | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| OWASP | A05:2025 Injection |
