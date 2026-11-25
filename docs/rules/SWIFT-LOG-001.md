# SWIFT-LOG-001: Sensitive data written to the log (Swift/iOS)

[Back to the rules catalog](index.md)

## What it detects

Logging of sensitive data: print, NSLog, os_log or a logger receives a variable that looks like a token, password, PIN or card data. The iOS unified log can be read with Console.app and a connected device, appears in sysdiagnose, and reaches crash reporting tools. With Logger, privacy: .public deliberately leaves it visible.

## How to fix it

Do not log tokens, passwords, PINs, card numbers or Authorization headers. If you need to trace the value, log only its length or the last four characters. With Logger, keep the default privacy or use privacy: .private, and wrap debug traces in #if DEBUG.

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
| Stack | Swift |
| Languages | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Security Logging and Alerting Failures |
