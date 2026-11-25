# DART-WEB-002: WebView with JavaScript enabled (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

WebView with unrestricted JavaScript: any page it loads runs scripts with access to the WebView's cookies and content. This is common and necessary for many pages, but it should load only your own content over https.

## How to fix it

Enable JavaScript only if the page needs it, restrict navigation to your own domains with NavigationDelegate or shouldOverrideUrlLoading, and do not load content over http. For static content, use JavaScriptMode.disabled.

## Why it matters

This rule maps to [CWE-749](https://cwe.mitre.org/data/definitions/749.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check which app functions the WebView page can call. They should be the minimum, with the page limited to your domain over https and every message validated.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Dart and Flutter |
| Languages | `dart` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
