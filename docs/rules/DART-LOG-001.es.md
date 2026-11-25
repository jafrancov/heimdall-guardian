# DART-LOG-001: Dato sensible escrito en el registro (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Registro de datos sensibles: print, debugPrint, log o un logger reciben una variable que parece un token, contraseña, PIN o dato de tarjeta. Los registros se leen con adb logcat o la consola del dispositivo, y llegan a herramientas de reporte de fallos.

## Cómo corregirlo

No registrar tokens, contraseñas, PIN, números de tarjeta ni encabezados Authorization. Si hace falta rastrear el valor, registrar solo su longitud o los últimos cuatro caracteres, y proteger los registros de depuración con kDebugMode.

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
| Stack | Dart y Flutter |
| Lenguajes | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Fallas de registro y alertas de seguridad |
