# PHP-SQL-002: Inyección SQL a través de un parámetro de función (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Un parámetro de esta función o método llega al texto SQL sin conversión ni escape. Quien la llame con datos de la petición (a menudo un controlador) abre una inyección SQL.

## Cómo corregirlo

Usa sentencias preparadas con parámetros enlazados ($stmt = $db-&gt;prepare(...); $stmt-&gt;bind_param(...)). Si debes armar el texto, convierte los números con (int) y escapa las cadenas con la función del controlador de la base de datos.

## Por qué importa

Esta regla corresponde a [CWE-89](https://cwe.mitre.org/data/definitions/89.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si la consulta se arma uniendo texto con datos del usuario. Debe usar parámetros enlazados; comprueba que ningún dato llegue a la consulta como texto.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
