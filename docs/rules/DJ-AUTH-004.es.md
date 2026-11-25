# DJ-AUTH-004: Protección CSRF desactivada (@csrf_exempt)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Protección CSRF desactivada. Un sitio externo puede hacer que el navegador de un usuario autenticado ejecute esta operación sin que lo sepa.

## Cómo corregirlo

Quitar csrf_exempt y enviar el token CSRF desde el cliente. Para APIs consumidas por otros sistemas, usar autenticación por token en lugar de sesión.

## Por qué importa

Esta regla corresponde a [CWE-352](https://cwe.mitre.org/data/definitions/352.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Comprueba si la acción cambia datos y si exige un token anti-CSRF o una cookie con SameSite. Prueba enviar la petición desde otro sitio en pruebas.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONTROL ACCESO |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-352](https://cwe.mitre.org/data/definitions/352.html) |
| OWASP | A01:2025 Control de acceso roto |
