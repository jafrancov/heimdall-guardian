# PHP-CRY-001: Contraseñas con md5/sha1 (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Contraseña protegida con md5() o sha1(). Son funciones rápidas y sin sal: las contraseñas se recuperan en minutos si la base de datos se filtra.

## Cómo corregirlo

Usar password_hash() al guardar y password_verify() al comprobar, y migrar las contraseñas existentes en el siguiente inicio de sesión.

## Por qué importa

Esta regla corresponde a [CWE-916](https://cwe.mitre.org/data/definitions/916.html) y a la categoría A04:2025 Fallas criptográficas del OWASP Top 10:2025.

## Cómo verificarlo

Revisa cómo se guardan las contraseñas: deben usar un algoritmo lento con sal (Argon2, bcrypt o scrypt), nunca MD5, SHA-1 ni SHA-256 simple.

## Datos

| | |
|---|---|
| Severidad | ALTA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-916](https://cwe.mitre.org/data/definitions/916.html) |
| OWASP | A04:2025 Fallas criptográficas |
