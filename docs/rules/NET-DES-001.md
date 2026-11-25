# NET-DES-001: Insecure deserialization (.NET)

[Back to the rules catalog](index.md)

## What it detects

Insecure deserializer. BinaryFormatter, NetDataContractSerializer and TypeNameHandling.All allow arbitrary types to be instantiated and can lead to remote code execution when processing untrusted data.

## How to fix it

Replace with System.Text.Json or with DataContractSerializer using known types. In Json.NET, use TypeNameHandling.None.

## Why it matters

This rule maps to [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and to the OWASP Top 10:2025 category A08:2025 Software or Data Integrity Failures.

## How to verify it

Identify where the deserialized data comes from. If it is not fully trusted, use a simple data format (JSON) with schema validation.

## Facts

| | |
|---|---|
| Severity | HIGH |
| Confidence | HIGH |
| Category | SAST |
| Stack | .NET |
| Languages | `csharp` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Software or Data Integrity Failures |
