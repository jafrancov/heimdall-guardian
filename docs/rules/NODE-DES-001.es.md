# NODE-DES-001: Deserialización insegura (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Deserialización insegura: node-serialize.unserialize ejecuta funciones incluidas en el texto, js-yaml con el esquema completo construye objetos y funciones arbitrarias, y evaluar JSON con eval ejecuta cualquier código incluido en él.

## Cómo corregirlo

No usar node-serialize: intercambiar datos como JSON con JSON.parse. En js-yaml usar yaml.load con el esquema por defecto de la versión 4 o DEFAULT_SCHEMA/JSON_SCHEMA, nunca DEFAULT_FULL_SCHEMA. No evaluar JSON con eval.

## Por qué importa

Esta regla corresponde a [CWE-502](https://cwe.mitre.org/data/definitions/502.html) y a la categoría A08:2025 Fallas de integridad de software o datos del OWASP Top 10:2025.

## Cómo verificarlo

Identifica de dónde vienen los datos que se deserializan. Si no son de confianza total, usa un formato de datos simple (JSON) con validación de esquema.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Fallas de integridad de software o datos |
