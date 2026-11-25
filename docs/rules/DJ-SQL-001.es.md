# DJ-SQL-001: SQL dinámico en consulta directa (Django)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Consulta SQL construida con f-string, formato % o concatenación. Si algún valor proviene del usuario, permite inyección SQL.

## Cómo corregirlo

Usar consultas parametrizadas: cursor.execute("... WHERE id = %s", [valor]) o el ORM. Nunca interpolar valores en el texto de la consulta.

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
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
