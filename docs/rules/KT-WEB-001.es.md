# KT-WEB-001: WebView con addJavascriptInterface (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

El WebView expone un objeto de la aplicación al JavaScript de la página (addJavascriptInterface). Si la página carga contenido de un tercero, o si el WebView sigue enlaces, un script malicioso puede invocar los métodos anotados con @JavascriptInterface y alcanzar funciones nativas de la aplicación.

## Cómo corregirlo

Evitar el puente. Si es indispensable, limitar el WebView a páginas propias por https (validar cada navegación en shouldOverrideUrlLoading), exponer solo métodos mínimos con @JavascriptInterface, validar cada argumento y no exponer datos sensibles. Para mensajería con la página, preferir WebViewCompat.addWebMessageListener con orígenes permitidos.

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
| Stack | Kotlin y Android |
| Lenguajes | `kotlin` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
