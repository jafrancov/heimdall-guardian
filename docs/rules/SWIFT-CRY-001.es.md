# SWIFT-CRY-001: Criptografía débil o vector de inicialización fijo (Swift/iOS)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Criptografía débil: MD5 o SHA-1 aplicados a contraseñas, cifrado en modo ECB, vector de inicialización (IV) fijo o un generador aleatorio predecible para tokens, códigos o contraseñas. Las contraseñas se descifran por fuerza bruta, ECB delata patrones del texto cifrado y un IV repetido anula la protección del modo CBC o GCM.

## Cómo corregirlo

Para contraseñas, usar un algoritmo lento con sal (Argon2, bcrypt o PBKDF2 con CCKeyDerivationPBKDF) y, de preferencia, verificarlas en el servidor. Para cifrar, AES.GCM de CryptoKit, que genera un nonce aleatorio nuevo por mensaje; nunca ECB ni IV literales. Para tokens y códigos, SecRandomCopyBytes o SystemRandomNumberGenerator, no rand() ni random().

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
| Stack | Swift |
| Lenguajes | `swift` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Fallas criptográficas |
