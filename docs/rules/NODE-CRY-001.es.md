# NODE-CRY-001: Criptografía débil o aleatoriedad predecible (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Criptografía débil: hash MD5 o SHA-1 aplicado a contraseñas, Math.random() para generar tokens o contraseñas (no es criptográficamente seguro), createCipher sin vector de inicialización o cifrado en modo ECB o DES.

## Cómo corregirlo

Para contraseñas usar bcrypt, scrypt (crypto.scrypt) o argon2. Para tokens, crypto.randomBytes o crypto.randomUUID. Para cifrar, createCipheriv con AES-256-GCM y un IV aleatorio por mensaje; nunca ECB.

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
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Fallas criptográficas |
