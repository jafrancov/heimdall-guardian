# KT-LOG-001: Sensitive data written to the log (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

Logging of sensitive data: Log, Timber or println receives a variable that looks like a token, password, PIN or card data. The Android log can be read with adb logcat, is included in bug reports and, before Android 4.1, could be read by other applications.

## How to fix it

Do not log tokens, passwords, PINs, card numbers or Authorization headers. If you need to trace the value, log only its length or the last four characters. Plant Timber with a debug tree only under BuildConfig.DEBUG, and strip Log calls with R8/ProGuard rules (-assumenosideeffects) in the released version.

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
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Security Logging and Alerting Failures |
