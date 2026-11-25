# DART-SQL-001: Consulta SQL construida con texto (sqflite/drift, Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Inyección SQL: la consulta se arma con interpolación ($variable o ${expresión}) o concatenación de texto en lugar de argumentos enlazados. Un valor como `' OR 1=1 --` altera la consulta y puede leer o borrar la base local de la aplicación.

## Cómo corregirlo

Usar marcadores ? con la lista de argumentos (rawQuery('... WHERE id = ?', [id])), los parámetros where/whereArgs de query, update y delete, o las consultas tipadas de drift. En drift, Variable&lt;T&gt; dentro de customSelect. Nunca interpolar valores en el SQL.

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
| Stack | Dart y Flutter |
| Lenguajes | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
