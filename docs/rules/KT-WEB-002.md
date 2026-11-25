# KT-WEB-002: WebView with local file access or an address taken from an Intent (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

WebView configuration that widens what a page can do: access to local files (allowFileAccess, allowFileAccessFromFileURLs, allowUniversalAccessFromFileURLs) or loading an address that arrives in an Intent. A malicious HTML file saved in the application or an Intent from another application can read the app's own files or open attacker-controlled pages.

## How to fix it

Leave allowFileAccess, allowFileAccessFromFileURLs and allowUniversalAccessFromFileURLs set to false and serve local content with WebViewAssetLoader. Before calling loadUrl with data from an Intent, validate the https scheme and that the host is on an allowlist.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Insecure Design |
