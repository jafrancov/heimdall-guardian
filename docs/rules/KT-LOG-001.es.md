# KT-LOG-001: Dato sensible escrito en el registro (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Registro de datos sensibles: Log, Timber o println reciben una variable que parece un token, contraseña, PIN o dato de tarjeta. El registro de Android se lee con adb logcat, se incluye en reportes de error y, en versiones anteriores a Android 4.1, lo leían otras aplicaciones.

## Cómo corregirlo

No registrar tokens, contraseñas, PIN, números de tarjeta ni encabezados Authorization. Si hace falta rastrear el valor, registrar solo su longitud o los últimos cuatro caracteres. Plantar Timber con un árbol de depuración solo en BuildConfig.DEBUG, y quitar las llamadas a Log con reglas de R8/ProGuard (-assumenosideeffects) en la versión publicada.

## Por qué importa

Esta regla corresponde a [CWE-532](https://cwe.mitre.org/data/definitions/532.html) y a la categoría A09:2025 Fallas de registro y alertas de seguridad del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué valores llegan a print, debugPrint o al logger. Los tokens, contraseñas y datos de tarjeta no deben aparecer; prueba la app y lee el registro con `adb logcat`.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Fallas de registro y alertas de seguridad |
