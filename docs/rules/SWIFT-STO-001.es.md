# SWIFT-STO-001: Token o contraseña en UserDefaults o @AppStorage (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Dato sensible guardado en UserDefaults o en @AppStorage: se escribe en un archivo plist sin cifrar que se incluye en las copias de seguridad del dispositivo y se lee sin esfuerzo con un dispositivo con jailbreak o desde una copia extraída.

## Cómo corregirlo

Guardar tokens, contraseñas, PIN y llaves en el Keychain (SecItemAdd, con kSecAttrAccessibleWhenUnlockedThisDeviceOnly o kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly) y no en UserDefaults ni en @AppStorage. Conservar en el dispositivo solo lo imprescindible y con vigencia corta.

## Por qué importa

Esta regla corresponde a [CWE-312](https://cwe.mitre.org/data/definitions/312.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Revisa dónde se guarda el dato: en el dispositivo, SharedPreferences y GetStorage son archivos legibles. Los datos sensibles deben ir en el llavero (flutter_secure_storage).

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Fallas criptográficas |
