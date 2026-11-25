# PHP-DES-001: Deserialización de datos de la petición (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

unserialize() sobre datos de la petición: permite instanciar objetos arbitrarios y puede derivar en ejecución remota de código.

## Cómo corregirlo

Intercambiar datos con json_decode(). Si unserialize() es indispensable, usar ['allowed_classes' =&gt; false] y firmar el contenido.

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
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) |
| OWASP | A08:2025 Fallas de integridad de software o datos |
