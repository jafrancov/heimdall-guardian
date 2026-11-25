# NODE-SQL-001: Inyección SQL con datos de la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Datos de la petición (req.query, req.body, req.params, cabeceras o parámetros de NestJS) llegan a una consulta SQL construida con concatenación o plantilla: permite inyección SQL.

## Cómo corregirlo

Usar consultas parametrizadas: db.query('SELECT ... WHERE id = $1', [id]) o db.query('... WHERE id = ?', [id]); con Prisma, $queryRaw como plantilla etiquetada; con Sequelize, replacements o bind; con Knex, bindings o el constructor de consultas. Nunca interpolar valores en el texto de la consulta.

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
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| OWASP | A05:2025 Inyección |
