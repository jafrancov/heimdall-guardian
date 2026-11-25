# KT-SQL-001: Consulta SQL construida con texto (SQLite o Room, Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Inyección SQL: la consulta de SQLite o de Room se arma con una plantilla de texto ($valor, ${valor}) o con concatenación en lugar de argumentos enlazados. Un valor como `' OR 1=1 --` altera la consulta y puede leer o borrar la base local de la aplicación; si la consulta está expuesta por un ContentProvider, también la de otras aplicaciones.

## Cómo corregirlo

Usar marcadores ? con la lista de argumentos (db.rawQuery("... WHERE id = ?", arrayOf(id)), o SimpleSQLiteQuery("... ?", arrayOf(id)) en Room) o, mejor, consultas @Query con parámetros :nombre. Nunca interpolar ni concatenar valores en el SQL; los nombres de tabla o columna variables se validan contra una lista fija.

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
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
