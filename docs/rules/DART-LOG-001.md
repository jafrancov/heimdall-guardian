# DART-LOG-001: Sensitive data written to the log (Dart/Flutter)

[Back to the rules catalog](index.md)

## What it detects

Logging of sensitive data: print, debugPrint, log or a logger receives a variable that looks like a token, password, PIN or card data. Logs can be read with adb logcat or the device console, and they reach crash reporting tools.

## How to fix it

Do not log tokens, passwords, PINs, card numbers or Authorization headers. If you need to trace the value, log only its length or the last four characters, and protect debug logs with kDebugMode.

## Why it matters

This rule maps to [CWE-532](https://cwe.mitre.org/data/definitions/532.html) and to the OWASP Top 10:2025 category A09:2025 Security Logging and Alerting Failures.

## How to verify it

Check which values reach print, debugPrint or the logger. Tokens, passwords and card data should not appear; run the app and read the log with `adb logcat`.

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | MEDIUM |
| Category | SAST |
| Stack | Dart and Flutter |
| Languages | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Security Logging and Alerting Failures |
