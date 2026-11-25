# PHP-MAS-001: Asignación masiva (Laravel)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Asignación masiva: se guardan todos los campos de la petición, o el modelo no protege ninguno. Un usuario puede modificar campos que no debería, como el rol o el propietario del registro.

## Cómo corregirlo

Usar $request-&gt;validated() o $request-&gt;only([...]) y declarar $fillable en el modelo con los campos permitidos.

## Por qué importa

Esta regla corresponde a [CWE-915](https://cwe.mitre.org/data/definitions/915.html) y a la categoría A06:2025 Diseño inseguro del OWASP Top 10:2025.

## Cómo verificarlo

Revisa qué campos acepta el modelo desde la petición. Debe existir una lista explícita de campos permitidos; comprueba que no se pueda enviar, por ejemplo, un rol.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-915](https://cwe.mitre.org/data/definitions/915.html) |
| OWASP | A06:2025 Diseño inseguro |
