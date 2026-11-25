# NODE-NOSQL-001: Inyección NoSQL con datos de la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Un valor de la petición se usa como filtro de MongoDB o Mongoose sin convertirlo a texto: un cuerpo JSON como {"$ne": null} cambia el sentido de la consulta (inyección NoSQL). El operador $where con datos de la petición permite además ejecutar JavaScript en la base.

## Cómo corregirlo

Convertir cada valor del filtro al tipo esperado antes de consultar (String(valor), Number(valor), new ObjectId(valor)), validar el cuerpo con un esquema (Joi, Zod, class-validator) o limpiar los operadores con express-mongo-sanitize. No usar $where con datos del usuario.

## Por qué importa

Esta regla corresponde a [CWE-943](https://cwe.mitre.org/data/definitions/943.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el filtro de la consulta se arma con objetos que envía el usuario. Debe validarse que cada valor sea del tipo esperado (texto, número) antes de usarlo.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-943](https://cwe.mitre.org/data/definitions/943.html) |
| OWASP | A05:2025 Inyección |
