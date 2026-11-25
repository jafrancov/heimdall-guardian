# NET-DES-001: Deserialización insegura (.NET)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Deserializador inseguro. BinaryFormatter, NetDataContractSerializer y TypeNameHandling.All permiten instanciar tipos arbitrarios y pueden derivar en ejecución remota de código al procesar datos no confiables.

## Cómo corregirlo

Sustituir por System.Text.Json o por DataContractSerializer con tipos conocidos. En Json.NET, usar TypeNameHandling.None.

## Por qué importa

Esta regla corresponde a [CWE-502](https://cwe.mitre.org/data/definitions/502.html) y a la categoría A08:2025 Fallas de integridad de software o datos del OWASP Top 10:2025.

## Cómo verificarlo

Identifica de dónde vienen los datos que se deserializan. Si no son de confianza total, usa un formato de datos simple (JSON) con validación de esquema.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | .NET |
| Lenguajes | `csharp` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Fallas de integridad de software o datos |
