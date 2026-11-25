# SWIFT-WEB-001: WKWebView with a JavaScript bridge to the application (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Bridge between JavaScript and the application: the page loaded by the WKWebView can send messages to native code through a WKScriptMessageHandler. If the page belongs to a third party, is loaded over http, or has foreign content injected into it, a malicious script gains access to application functions.

## How to fix it

Load only your own pages over https and, in the handler, check message.frameInfo.securityOrigin before answering. Expose the minimum of functions, validate and treat as untrusted every incoming message, and do not return session data. Remove the handler (removeScriptMessageHandler) when the view is no longer used.

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
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
