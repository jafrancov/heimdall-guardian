# NET-AUTH-002: Acción de escritura anónima ([AllowAnonymous])

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Acción de escritura (POST, PUT, PATCH o DELETE) marcada con [AllowAnonymous]: cualquiera puede modificar datos sin autenticarse.

## Cómo corregirlo

Quitar [AllowAnonymous] y exigir autenticación. Si debe ser pública (por ejemplo, el inicio de sesión), documentarlo y aceptar el hallazgo con justificación.

## Por qué importa

Esta regla corresponde a [CWE-306](https://cwe.mitre.org/data/definitions/306.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la ruta y sus decoradores, middleware o filtros globales. Prueba la petición sin credenciales en un entorno de pruebas: debe responder 401 o 403.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | CONTROL ACCESO |
| Stack | .NET |
| Lenguajes | `csharp` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Control de acceso roto |
