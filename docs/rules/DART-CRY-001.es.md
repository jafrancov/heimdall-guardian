# DART-CRY-001: Criptografía débil o aleatoriedad predecible (Dart/Flutter)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Criptografía débil: MD5 o SHA-1 aplicados a contraseñas, Random() (no criptográfico) para generar tokens, contraseñas, códigos o nonces, cifrado AES en modo ECB o vector de inicialización fijo. Las contraseñas se descifran por fuerza bruta, los valores aleatorios se predicen y un IV repetido revela patrones del texto cifrado.

## Cómo corregirlo

Para contraseñas, usar un algoritmo lento con sal (argon2, bcrypt o scrypt) en el servidor. Para tokens, códigos y nonces, Random.secure(). Para cifrar, AES en modo GCM (o CBC con HMAC) con un IV aleatorio nuevo por mensaje (IV.fromSecureRandom(16)); nunca ECB ni IV fijos.

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
| Stack | Dart y Flutter |
| Lenguajes | `dart` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Fallas criptográficas |
