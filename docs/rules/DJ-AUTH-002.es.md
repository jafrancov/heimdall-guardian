# DJ-AUTH-002: Vista sin autenticación (Django, CBV)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Vista basada en clase sin LoginRequiredMixin ni PermissionRequiredMixin. Si está publicada en urls.py, es accesible sin iniciar sesión.

## Cómo corregirlo

Heredar de LoginRequiredMixin o PermissionRequiredMixin como primera clase base. Si la vista debe ser pública, documentarlo y aceptar el hallazgo con justificación.

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
