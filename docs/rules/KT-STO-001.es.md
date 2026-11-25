# KT-STO-001: Token o contraseña en SharedPreferences o DataStore (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Dato sensible guardado en SharedPreferences o en DataStore sin cifrar: ambos escriben archivos legibles por quien tenga el dispositivo con root, por una copia de seguridad (adb backup, Auto Backup) o por otra aplicación con acceso a ese almacenamiento.

## Cómo corregirlo

Guardar tokens, contraseñas, PIN y llaves cifrados con una llave del Android Keystore: EncryptedSharedPreferences, o DataStore cifrado con Tink. Conservar en el dispositivo solo lo imprescindible, con vigencia corta, y excluir esos archivos de la copia de seguridad.

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
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Fallas criptográficas |
