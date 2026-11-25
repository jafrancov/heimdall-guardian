# NET-AUTH-001: Controlador sin [Authorize] (.NET)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Controlador sin [Authorize] en la clase ni en sus acciones. Salvo que exista un filtro global de autorización, sus acciones son accesibles sin iniciar sesión.

## Cómo corregirlo

Agregar [Authorize] al controlador, o configurar una política de autorización global (FallbackPolicy) y marcar con [AllowAnonymous] solo lo que deba ser público.

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
| Stack | .NET |
| Lenguajes | `csharp` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Control de acceso roto |
