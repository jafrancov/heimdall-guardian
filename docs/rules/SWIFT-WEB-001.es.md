# SWIFT-WEB-001: WKWebView con puente de JavaScript hacia la aplicación (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Puente entre JavaScript y la aplicación: la página que carga el WKWebView puede enviar mensajes al código nativo mediante un WKScriptMessageHandler. Si la página es de terceros, se carga por http o se le inyecta contenido ajeno, un script malicioso obtiene acceso a funciones de la aplicación.

## Cómo corregirlo

Cargar solo páginas propias por https y, en el manejador, comprobar message.frameInfo.securityOrigin antes de responder. Exponer el mínimo de funciones, validar y tratar como no confiable cada mensaje que llegue y no devolverle datos de sesión. Quitar el manejador (removeScriptMessageHandler) cuando la vista deje de usarse.

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
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
