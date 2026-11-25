# DJ-AUTH-003: API sin autenticación: AllowAny (DRF)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Django REST Framework configurado con AllowAny: el endpoint (o toda la API, si es el valor por defecto) acepta peticiones sin autenticación.

## Cómo corregirlo

Usar IsAuthenticated o un permiso específico. En settings, definir DEFAULT_PERMISSION_CLASSES con IsAuthenticated y abrir solo los endpoints que deban ser públicos.

## Por qué importa

Esta regla corresponde a [CWE-306](https://cwe.mitre.org/data/definitions/306.html) y a la categoría A01:2025 Control de acceso roto del OWASP Top 10:2025.

## Cómo verificarlo

Revisa la ruta y sus decoradores, middleware o filtros globales. Prueba la petición sin credenciales en un entorno de pruebas: debe responder 401 o 403.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | CONTROL ACCESO |
| Stack | Python y Django |
| Lenguajes | `python` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Control de acceso roto |
