# KT-WEB-001: WebView with addJavascriptInterface (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

The WebView exposes an application object to the page's JavaScript (addJavascriptInterface). If the page loads third-party content, or if the WebView follows links, a malicious script can invoke the methods annotated with @JavascriptInterface and reach native application functions.

## How to fix it

Avoid the bridge. If it is indispensable, restrict the WebView to your own pages over https (validate every navigation in shouldOverrideUrlLoading), expose only minimal methods with @JavascriptInterface, validate every argument and do not expose sensitive data. For messaging with the page, prefer WebViewCompat.addWebMessageListener with allowed origins.

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
| Stack | Kotlin and Android |
| Languages | `kotlin` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
