# SWIFT-SQL-001: Consulta SQL construida con texto (SQLite, GRDB o FMDB, Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Inyección SQL: la consulta se arma con interpolación (\(valor)) o concatenación de texto en lugar de argumentos enlazados. Un valor como `' OR 1=1 --` altera la consulta y puede leer o borrar la base local de la aplicación.

## Cómo corregirlo

Usar marcadores ? o :nombre con la lista de argumentos (db.execute(sql: "... WHERE id = ?", arguments: [id]) en GRDB, executeQuery("... ?", values: [id]) en FMDB, sqlite3_bind_* con sqlite3_prepare_v2). En GRDB, la interpolación solo es segura con SQL literal (execute(literal:) o la API de consulta tipada). Nunca interpolar valores en el SQL.

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
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
