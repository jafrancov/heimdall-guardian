# DART-STO-001: Token o contraseña en almacenamiento sin cifrar (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Dato sensible guardado en almacenamiento sin cifrar: SharedPreferences y GetStorage escriben archivos de texto legibles por quien tenga el dispositivo con root o jailbreak, o una copia de seguridad.

## Cómo corregirlo

Guardar tokens, contraseñas, PIN y llaves con flutter_secure_storage (Keychain en iOS, Keystore en Android) y no en SharedPreferences ni GetStorage. Conservar en el dispositivo solo lo imprescindible y con vigencia corta.

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
| Stack | Dart y Flutter |
| Lenguajes | `dart` |
| CWE | [CWE-312](https://cwe.mitre.org/data/definitions/312.html) |
| OWASP | A04:2025 Fallas criptográficas |
