# PHP-AUTH-002: Ruta sin middleware de autenticación (Laravel)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Ruta de Laravel declarada fuera de un grupo con middleware de autenticación: es accesible sin iniciar sesión.

## Cómo corregirlo

Declarar la ruta dentro de Route::middleware('auth')-&gt;group(...) o encadenar -&gt;middleware('auth'). Si debe ser pública, documentarlo y aceptar el hallazgo con justificación.

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
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-306](https://cwe.mitre.org/data/definitions/306.html) |
| OWASP | A01:2025 Control de acceso roto |
