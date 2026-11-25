# SWIFT-WEB-003: Deprecated and insecure UIWebView (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Use of UIWebView: Apple has deprecated it, the App Store rejects apps that include it, and it receives no security fixes. It does not isolate the page process or let you restrict JavaScript execution the way WKWebView does.

## How to fix it

Migrate to WKWebView (WebKit), which runs in a separate process and lets you control navigation with WKNavigationDelegate. To show external pages without custom code, use SFSafariViewController.

## Why it matters

This rule maps to [CWE-477](https://cwe.mitre.org/data/definitions/477.html) and to the OWASP Top 10:2025 category A03:2025 Software Supply Chain Failures.

## How to verify it

Find the obsolete component in the code and in the dependencies. Confirm in the vendor's documentation which one replaces it and which version no longer receives fixes.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | HIGH |
| Category | SAST |
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-477](https://cwe.mitre.org/data/definitions/477.html) |
| OWASP | A03:2025 Software Supply Chain Failures |
