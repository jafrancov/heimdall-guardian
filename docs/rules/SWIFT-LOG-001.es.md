# SWIFT-LOG-001: Dato sensible escrito en el registro (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Registro de datos sensibles: print, NSLog, os_log o un logger reciben una variable que parece un token, contraseña, PIN o dato de tarjeta. El registro unificado de iOS se lee con Console.app y con un dispositivo conectado, aparece en sysdiagnose y llega a herramientas de reporte de fallos. En Logger, privacy: .public lo deja visible a propósito.

## Cómo corregirlo

No registrar tokens, contraseñas, PIN, números de tarjeta ni encabezados Authorization. Si hace falta rastrear el valor, registrar solo su longitud o los últimos cuatro caracteres. Con Logger, dejar la privacidad por defecto o usar privacy: .private, y envolver las trazas de depuración en #if DEBUG.

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
| Stack | Swift |
| Lenguajes | `regex` |
| CWE | [CWE-532](https://cwe.mitre.org/data/definitions/532.html) |
| OWASP | A09:2025 Fallas de registro y alertas de seguridad |
