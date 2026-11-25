# KT-CRY-001: Algoritmo criptográfico débil, IV fijo o aleatorio inseguro (Kotlin/Android)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Criptografía débil: un resumen MD5 o SHA-1, un cifrado AES en modo ECB (o "AES" a secas, que en Android equivale a ECB), DES, 3DES, RC4 o Blowfish, un vector de inicialización (IV) fijo, o un generador no criptográfico (Random) para un token, contraseña, código o sal. Los datos protegidos así se pueden descifrar, falsificar o predecir.

## Cómo corregirlo

Cifrar con AES/GCM/NoPadding con una llave del Android Keystore y un IV nuevo y aleatorio en cada operación (guardarlo junto al texto cifrado). Resumir con SHA-256 o superior, y guardar contraseñas con un algoritmo lento (Argon2, bcrypt, PBKDF2 con muchas iteraciones). Para tokens y códigos, usar SecureRandom.

## Por qué importa

Esta regla corresponde a [CWE-327](https://cwe.mitre.org/data/definitions/327.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Identifica para qué se usa el algoritmo. Si protege contraseñas o datos, sustitúyelo por uno vigente (Argon2, bcrypt o scrypt; AES-GCM). MD5 o SHA-1 solo sirven para sumas de verificación sin valor de seguridad.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | Kotlin y Android |
| Lenguajes | `regex` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Fallas criptográficas |
