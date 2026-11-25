# PHP-CALL-001: Llamada dinámica con un nombre controlado por la petición (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

El nombre de una función, método o clase viene de la petición y se invoca de forma dinámica ($nombre(...), call_user_func, new $clase, $objeto-&gt;$metodo()). El visitante elige qué código se ejecuta, así que puede llegar a cualquier función de la aplicación o del propio PHP.

## Cómo corregirlo

No invocar nunca un nombre tomado de la petición. Asociar los valores aceptados con las funciones o clases permitidas (un arreglo fijo verificado con in_array($x, $lista, true) o array_key_exists) y rechazar todo lo demás antes de llamar. Verificar con function_exists o is_callable no basta: también acepta todas las funciones que ofrece PHP.

## Por qué importa

Esta regla corresponde a [CWE-94](https://cwe.mitre.org/data/definitions/94.html) y a la categoría A05:2025 Inyección del OWASP Top 10:2025.

## Cómo verificarlo

Busca si algún dato externo llega a una función que ejecuta código. Sustitúyela por una lista cerrada de operaciones permitidas.

## Datos

| | |
|---|---|
| Severidad | CRÍTICA |
| Confianza | MEDIA |
| Categoría | SAST |
| Stack | PHP y Laravel |
| Lenguajes | `php` |
| CWE | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| OWASP | A05:2025 Inyección |
