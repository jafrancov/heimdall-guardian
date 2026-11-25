# DART-WEB-001: WebView con puente de JavaScript hacia la aplicación (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Puente entre JavaScript y la aplicación: la página que carga el WebView puede llamar código nativo de Dart mediante un canal o manejador. Si la página es de terceros, si se carga por http o si se le inyecta contenido ajeno, un script malicioso obtiene acceso a funciones de la aplicación.

## Cómo corregirlo

Cargar solo páginas propias por https y validar el origen antes de responder a un mensaje (por ejemplo con NavigationDelegate). Exponer el mínimo de funciones, validar y tratar como no confiable cada mensaje que llegue del canal, y no devolverle datos de sesión.

## Por qué importa

Esta regla corresponde a [CWE-749](https://cwe.mitre.org/data/definitions/749.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué funciones de la aplicación puede invocar la página del WebView. Deben ser las mínimas, con la página limitada a tu dominio por https y cada mensaje validado.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Dart y Flutter |
| Lenguajes | `dart` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
