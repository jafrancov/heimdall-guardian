# DJ-CONF-004: Cookies o transporte inseguros en settings

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Cookies de sesión o CSRF sin la marca Secure, o redirección a HTTPS desactivada: las credenciales de sesión pueden viajar en claro.

## Cómo corregirlo

En producción: SESSION_COOKIE_SECURE = True, CSRF_COOKIE_SECURE = True y SECURE_SSL_REDIRECT = True, además de SECURE_HSTS_SECONDS.

## Por qué importa

Esta regla corresponde a [CWE-614](https://cwe.mitre.org/data/definitions/614.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Revisa los atributos de la cookie de sesión: debe llevar `Secure` y `HttpOnly`. Compruébalo en las herramientas del navegador.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | CONFIGURACION |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-614](https://cwe.mitre.org/data/definitions/614.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
