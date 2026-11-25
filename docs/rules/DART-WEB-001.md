# DART-WEB-001: WebView with a JavaScript bridge to the application (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

Bridge between JavaScript and the application: the page loaded by the WebView can call native Dart code through a channel or handler. If the page belongs to a third party, is loaded over http, or has foreign content injected into it, a malicious script gains access to application functions.

## How to fix it

Load only your own pages over https and validate the origin before answering a message (for example with NavigationDelegate). Expose the minimum of functions, validate and treat as untrusted every message that arrives from the channel, and do not return session data to it.

## Why it matters

This rule maps to [CWE-749](https://cwe.mitre.org/data/definitions/749.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check which app functions the WebView page can call. They should be the minimum, with the page limited to your domain over https and every message validated.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Dart and Flutter |
| Languages | `dart` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
