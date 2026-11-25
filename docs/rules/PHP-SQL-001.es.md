# PHP-SQL-001: Inyección SQL con datos de la petición (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición ($_GET, $_POST, $_REQUEST o $_COOKIE) llegan a una consulta SQL sin parametrizar: permite inyección SQL.

## Cómo corregirlo

Usar sentencias preparadas (PDO::prepare o mysqli_prepare con bind_param). Nunca concatenar datos de la petición en la consulta.

## Por qué importa

Esta regla corresponde a [CWE-89](https://cwe.mitre.org/data/definitions/89.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si la consulta se arma uniendo texto con datos del usuario. Debe usar parámetros enlazados; comprueba que ningún dato llegue a la consulta como texto.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
