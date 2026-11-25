# PHP-CAND-006: Deserialización de una variable (por revisar)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

> Candidata: solo la revisa la IA local, nunca se reporta sola

Se deserializan datos de un valor que no es constante. Es solo un punto por revisar: la IA local comprueba si le llega entrada no confiable.

## Cómo corregirlo

Nunca deserialices datos no confiables con un formato que pueda construir objetos arbitrarios; usa un formato de solo datos como JSON con un esquema fijo, o restringe los tipos permitidos.

## Por qué importa

Esta regla corresponde a [CWE-502](https://cwe.mitre.org/data/definitions/502.html) y a la categoría A08:2025 Fallas de integridad de software o datos del OWASP Top 10:2025.

## Cómo verificarlo

Identifica de dónde vienen los datos que se deserializan. Si no son de confianza total, usa un formato de datos simple (JSON) con validación de esquema.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Fallas de integridad de software o datos |
