# NODE-JWT-002: Secreto JWT escrito en el código (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

El secreto con que se firman o verifican los tokens JWT está escrito en el código. Quien lea el repositorio puede emitir tokens válidos.

## Cómo corregirlo

Leer el secreto de una variable de entorno o de un gestor de secretos (process.env.JWT_SECRET), usar un valor largo y aleatorio, y rotar el que ya estuvo en el repositorio. Para firmar con clave asimétrica, cargar la clave privada desde un archivo fuera del código.

## Por qué importa

Esta regla corresponde a [CWE-798](https://cwe.mitre.org/data/definitions/798.html) y a la categoría A07:2025 Fallas de autenticación del OWASP Top 10:2025.

## Cómo verificarlo

Busca el valor en el historial de versiones y confirma si sigue vigente. Si lo está, rótalo de inmediato y muévelo a un gestor de secretos.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) |
| OWASP | A07:2025 Fallas de autenticación |
