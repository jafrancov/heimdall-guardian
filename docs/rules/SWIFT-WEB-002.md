# SWIFT-WEB-002: WKWebView with universal access to local files (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

The WKWebView lets a page opened from a local file read other files on the device (allowFileAccessFromFileURLs) or from any origin (allowUniversalAccessFromFileURLs). A malicious HTML file saved or downloaded in the application can read its files and send them to an external server.

## How to fix it

Do not enable allowFileAccessFromFileURLs or allowUniversalAccessFromFileURLs. To display local content, use loadFileURL(_:allowingReadAccessTo:) with the minimum necessary folder, and load remote content over https only.

## Why it matters

This rule maps to [CWE-749](https://cwe.mitre.org/data/definitions/749.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check which app functions the WebView page can call. They should be the minimum, with the page limited to your domain over https and every message validated.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | Swift |
| Languages | `swift` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
