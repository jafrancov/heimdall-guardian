# DJ-UPL-001: File upload without type or size validation

[Back to the rules catalog](index.md)

## What it detects

File upload field without validators. With no limit on type or size, executables, HTML with scripts or files that exhaust storage can be uploaded.

## How to fix it

Add validators (FileExtensionValidator and a size validator) and check the real content of the file, not just its extension.

## Why it matters

This rule maps to [CWE-434](https://cwe.mitre.org/data/definitions/434.html) and to the OWASP Top 10:2025 category A06:2025 Insecure Design.

## How to verify it

Check the validation of the uploaded file: real type, allowed extension, maximum size, regenerated name and a folder outside the one the web server serves.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Python and Django |
| Languages | `python` |
| CWE | [CWE-434](https://cwe.mitre.org/data/definitions/434.html) |
| OWASP | A06:2025 Insecure Design |
