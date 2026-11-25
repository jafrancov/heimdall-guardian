# KT-STO-002: Archivo o preferencias con permisos para otras aplicaciones (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Un archivo o preferencia se crea con MODE_WORLD_READABLE o MODE_WORLD_WRITEABLE: cualquier otra aplicación del dispositivo puede leerlo o modificarlo. Android moderno lanza una excepción, pero en versiones anteriores el archivo queda abierto.

## Cómo corregirlo

Usar MODE_PRIVATE. Para compartir un archivo con otra aplicación, exponerlo con un FileProvider y permisos de URI temporales, y no con permisos de archivo globales.

## Por qué importa

Esta regla corresponde a [CWE-732](https://cwe.mitre.org/data/definitions/732.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa los permisos del archivo o recurso: solo debe poder leerlo o escribirlo quien lo necesita.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-732](https://cwe.mitre.org/data/definitions/732.html) |
| OWASP | A01:2025 Control de acceso roto |
