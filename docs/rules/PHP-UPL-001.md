# PHP-UPL-001: Uploaded file stored under a client-controlled path (PHP)

[Back to the rules catalog](index.md)

## What it detects

An uploaded file is stored under a path built from data the client controls (the original file name, the extension, a form field or the name of the upload field). The visitor decides the name and the folder, so a script can end up in a folder where the web server runs PHP, and an existing file can be overwritten.

## How to fix it

Generate the stored name on the server (for example random_bytes) and derive the extension from an allowlist, not from the original name. Check the extension and the real MIME type against an allowlist before moving the file, and store it outside the web root or in a folder where PHP does not run. If the folder comes from the request, pick it from a fixed list or check with realpath() that it stays inside the upload root.

## Why it matters

This rule maps to [CWE-434](https://cwe.mitre.org/data/definitions/434.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check the validation of the uploaded file: real type, allowed extension, maximum size, regenerated name and a folder outside the one the web server serves.

## Facts

| | |
|---|---|
| Severity | CRITICAL |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | PHP and Laravel |
| Languages | `php` |
| CWE | [CWE-434](https://cwe.mitre.org/data/definitions/434.html) |
| OWASP | A06:2025 Insecure Design |
