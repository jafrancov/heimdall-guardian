# NODE-JWT-003: Token JWT decodificado sin verificar la firma (Node.js)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Se decodifica un token JWT sin verificar su firma en la misma función. decode solo lee el contenido: cualquiera puede fabricar un token que diga lo que quiera.

## Cómo corregirlo

Usar jwt.verify (o jwtService.verify) para decidir si la persona está autenticada y para leer sus datos; reservar decode para información que no se use en decisiones de seguridad.

## Por qué importa

Esta regla corresponde a [CWE-345](https://cwe.mitre.org/data/definitions/345.html) y a la categoría A07:2025 Fallas de autenticación del OWASP Top 10:2025.

## Cómo verificarlo

Revisa si el dato se acepta sin comprobar su origen o integridad. Debe verificarse una firma o un código de autenticación antes de usarlo.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | BAJA |
| Categoría | SAST |
| Stack | Node.js y TypeScript |
| Lenguajes | `javascript`, `typescript` |
| CWE | [CWE-345](https://cwe.mitre.org/data/definitions/345.html) |
| OWASP | A07:2025 Fallas de autenticación |
