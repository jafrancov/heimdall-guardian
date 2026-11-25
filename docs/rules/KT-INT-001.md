# KT-INT-001: Mutable PendingIntent, exposed receiver or broadcast without permission (Kotlin/Android)

[Back to the rules catalog](index.md)

## What it detects

Inter-component communication that another application can abuse: a PendingIntent without FLAG_IMMUTABLE (an application that receives it can fill in or change its Intent and act with this app's permissions), a receiver registered without RECEIVER_NOT_EXPORTED that accepts messages from any application, or a sendBroadcast with sensitive data and no permission that any installed application can receive.

## How to fix it

Create PendingIntents with PendingIntent.FLAG_IMMUTABLE (use FLAG_MUTABLE only when the system must fill it in, and then with an explicit Intent). Register internal receivers with ContextCompat.registerReceiver(..., ContextCompat.RECEIVER_NOT_EXPORTED). For broadcasts with sensitive data, use an explicit Intent (setPackage) or sendBroadcast(intent, permission) with your own signature-level permission.

## Why it matters

This rule maps to [CWE-927](https://cwe.mitre.org/data/definitions/927.html) and to the OWASP Top 10:2025 category A01:2025 Broken Access Control.

## How to verify it

Look for PendingIntents and confirm they carry FLAG_IMMUTABLE and an explicit Intent. For broadcasts, confirm that what is sent is not sensitive or that only your app receives it (setPackage or a signature permission).

## Facts

| | |
|---|---|
| Severity | MEDIUM |
| Confidence | LOW |
| Category | SAST |
| Stack | Kotlin and Android |
| Languages | `regex` |
| CWE | [CWE-927](https://cwe.mitre.org/data/definitions/927.html) |
| OWASP | A01:2025 Broken Access Control |
