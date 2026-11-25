# NODE-CONF-001: CORS abierto a cualquier origen con credenciales (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

CORS permisivo con credenciales: el servidor acepta peticiones con cookies o cabeceras de autenticación desde cualquier sitio (origin '*', true, o el origen reflejado de la petición). Una página ajena puede actuar en nombre de la persona autenticada.

## Cómo corregirlo

Declarar una lista cerrada de orígenes permitidos (origin: ['https://app.ejemplo.com']) o una función que la consulte, y activar credentials solo para ellos. Nunca reflejar el origen de la petición sin comprobarlo.

## Por qué importa

Esta regla corresponde a [CWE-942](https://cwe.mitre.org/data/definitions/942.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la configuración de CORS: los orígenes deben ser una lista concreta; un origen abierto con credenciales permite que otros sitios lean datos de sesión.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-942](https://cwe.mitre.org/data/definitions/942.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
