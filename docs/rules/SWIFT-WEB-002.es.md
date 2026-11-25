# SWIFT-WEB-002: WKWebView con acceso universal a archivos locales (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

El WKWebView permite que una página abierta desde un archivo local lea otros archivos del dispositivo (allowFileAccessFromFileURLs) o cualquier origen (allowUniversalAccessFromFileURLs). Un HTML malicioso guardado o descargado en la aplicación puede leer sus archivos y enviarlos a un servidor externo.

## Cómo corregirlo

No activar allowFileAccessFromFileURLs ni allowUniversalAccessFromFileURLs. Para mostrar contenido local, usar loadFileURL(_:allowingReadAccessTo:) con la carpeta mínima necesaria, y cargar el contenido remoto solo por https.

## Por qué importa

Esta regla corresponde a [CWE-749](https://cwe.mitre.org/data/definitions/749.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué funciones de la aplicación puede invocar la página del WebView. Deben ser las mínimas, con la página limitada a tu dominio por https y cada mensaje validado.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | ALTA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-749](https://cwe.mitre.org/data/definitions/749.html) |
| OWASP | A06:2025 Diseño inseguro |
