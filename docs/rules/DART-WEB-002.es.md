# DART-WEB-002: WebView con JavaScript habilitado (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

WebView con JavaScript sin restricción: cualquier página que cargue ejecuta scripts con acceso a las cookies y al contenido del WebView. Es habitual y necesario para muchas páginas, pero conviene que cargue solo contenido propio y por https.

## Cómo corregirlo

Activar JavaScript solo si la página lo necesita, limitar la navegación a dominios propios con NavigationDelegate o shouldOverrideUrlLoading, y no cargar contenido por http. Para contenido estático, usar JavaScriptMode.disabled.

## Por qué importa

Esta regla corresponde a [CWE-749](https://cwe.mitre.org/data/definitions/749.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué funciones de la aplicación puede invocar la página del WebView. Deben ser las mínimas, con la página limitada a tu dominio por https y cada mensaje validado.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Dart y Flutter |
| Lenguajes | `dart` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
