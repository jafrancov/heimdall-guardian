# NODE-CONF-002: Cookie de sesión insegura o secreto de sesión en el código (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Sesión o cookie insegura: cookie sin httpOnly o sin secure, o secreto de sesión escrito en el código. Un script inyectado puede leer la cookie, viaja por conexiones sin cifrar, y quien lea el repositorio puede falsificar sesiones.

## Cómo corregirlo

Configurar httpOnly: true, secure: true (detrás de HTTPS, con trust proxy si aplica) y sameSite: 'lax' o 'strict'. Leer el secreto de sesión de una variable de entorno (process.env.SESSION_SECRET).

## Por qué importa

Esta regla corresponde a [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa los atributos de la cookie de sesión: debe llevar `HttpOnly` para que los scripts de la página no la lean.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
