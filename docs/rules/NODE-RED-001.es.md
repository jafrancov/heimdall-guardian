# NODE-RED-001: Redirección abierta con datos de la petición (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Un dato de la petición decide a dónde redirige el servidor (res.redirect, res.location). Un enlace manipulado puede llevar a la persona a un sitio falso con la apariencia de la aplicación (redirección abierta).

## Cómo corregirlo

Redirigir solo a rutas relativas propias: comprobar que el destino empiece con una sola diagonal (y no con // ni con un esquema) o compararlo contra una lista blanca de destinos y hosts.

## Por qué importa

Esta regla corresponde a [CWE-601](https://cwe.mitre.org/data/definitions/601.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el destino de la redirección sale de un dato de la petición. Debe compararse con una lista de destinos permitidos o limitarse a rutas internas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-601](https://cwe.mitre.org/data/definitions/601.html) |
| OWASP | A01:2025 Control de acceso roto |
