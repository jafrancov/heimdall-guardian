# SWIFT-DES-001: Deserialización sin restricción de clases con NSKeyedUnarchiver (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Deserialización insegura con NSKeyedUnarchiver: unarchiveObject(with:) no restringe las clases que reconstruye, y requiresSecureCoding en false lo permite explícitamente. Datos manipulados (un archivo compartido, un respaldo, un portapapeles) pueden instanciar clases inesperadas y alterar el comportamiento de la aplicación.

## Cómo corregirlo

Usar NSKeyedUnarchiver.unarchivedObject(ofClass:from:) o unarchivedObject(ofClasses:from:) con la lista mínima de clases permitidas, y mantener requiresSecureCoding en true. Para datos propios, preferir Codable con JSONDecoder.

## Por qué importa

Esta regla corresponde a [CWE-502](https://cwe.mitre.org/data/definitions/502.html) y a la categoría A08:2025 Fallas de integridad de software o datos del OWASP Top 10:2025.

## Cómo verificarlo

Identifica de dónde vienen los datos que se deserializan. Si no son de confianza total, usa un formato de datos simple (JSON) con validación de esquema.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Fallas de integridad de software o datos |
