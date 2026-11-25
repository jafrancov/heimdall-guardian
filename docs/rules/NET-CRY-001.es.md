# NET-CRY-001: Criptografía débil (.NET)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Algoritmo criptográfico débil (MD5, SHA-1, DES o 3DES). No es apto para proteger contraseñas ni datos sensibles.

## Cómo corregirlo

Para contraseñas, usar PasswordHasher de ASP.NET Identity o Rfc2898DeriveBytes (PBKDF2). Para cifrado, AES; para integridad, SHA-256 o superior.

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
| Stack | .NET |
| Lenguajes | `csharp` |
| CWE | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| OWASP | A04:2025 Fallas criptográficas |
