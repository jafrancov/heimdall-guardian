# PHP-INC-001: Inclusión de archivo con ruta variable (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

include/require con una ruta que depende de una variable. Si el valor proviene del usuario, permite incluir archivos arbitrarios y ejecutar código.

## Cómo corregirlo

Incluir solo rutas fijas. Si la página depende de un parámetro, resolverlo contra una lista blanca de archivos permitidos.

## Por qué importa

Esta regla corresponde a [CWE-98](https://cwe.mitre.org/data/definitions/98.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si la ruta del archivo incluido depende de un dato externo. Debe elegirse de una lista fija, nunca construirse con la entrada.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-98](https://cwe.mitre.org/data/definitions/98.html) |
| OWASP | A05:2025 Inyección |
