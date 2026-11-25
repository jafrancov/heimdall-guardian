# DJ-AUTH-001: Vista sin autenticación (Django, FBV)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Vista basada en función sin decorador de autenticación ni de permisos. Si está publicada en urls.py, cualquier persona puede invocarla sin iniciar sesión.

## Cómo corregirlo

Agregar @login_required o @permission_required. Si la vista debe ser pública (por ejemplo, el inicio de sesión), documentarlo y aceptar el hallazgo con justificación.

## Por qué importa

Esta regla corresponde a [CWE-306](https://cwe.mitre.org/data/definitions/306.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la ruta y sus decoradores, middleware o filtros globales. Prueba la petición sin credenciales en un entorno de pruebas: debe responder 401 o 403.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | BAJA |
| Categoría | CONTROL ACCESO |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Control de acceso roto |
