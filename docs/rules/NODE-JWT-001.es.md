# NODE-JWT-001: JWT con algoritmo none o sin validar la expiración (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Verificación o emisión de tokens JWT debilitada: se acepta el algoritmo none (sin firma) o se ignora la expiración del token.

## Cómo corregirlo

Fijar una lista cerrada de algoritmos firmados (por ejemplo algorithms: ['HS256'] o ['RS256']), nunca incluir none, y no usar ignoreExpiration: true. Si se necesita renovar un token vencido, hacerlo con un token de refresco.

## Por qué importa

Esta regla corresponde a [CWE-347](https://cwe.mitre.org/data/definitions/347.html) y a la categoría A07:2025 Fallas de autenticación del OWASP Top 10:2025.

## Cómo verificarlo

Revisa cómo se decodifica el token: debe verificarse la firma con la clave correcta y un algoritmo fijo, nunca el que indique el propio token.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-347](https://cwe.mitre.org/data/definitions/347.html) |
| OWASP | A07:2025 Fallas de autenticación |
