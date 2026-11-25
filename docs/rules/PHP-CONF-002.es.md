# PHP-CONF-002: Bandera de producción o depuración fija en el código (PHP)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

La bandera de producción o de depuración está escrita en el código PHP (PRODUCTION = false, DEBUG = true). Sin importar lo que diga el php.ini del servidor, el código que muestra errores o activa la depuración a partir de esta bandera lo hace también en producción, y nadie lo nota hasta que el archivo se cambia a mano en cada despliegue.

## Cómo corregirlo

Leer el ambiente de la configuración del servidor (una variable de entorno o un archivo fuera del repositorio) y, si falta, usar el comportamiento de producción. No versionar un valor de depuración que cambie lo que la aplicación muestra a los visitantes.

## Por qué importa

Esta regla corresponde a [CWE-489](https://cwe.mitre.org/data/definitions/489.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Confirma en el entorno de producción que el modo de depuración está apagado y que ninguna consola de desarrollo es accesible.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | MEDIA |
| Categoría | CONFIGURACION |
| Stack | PHP y Laravel |
| Lenguajes | `regex` |
| CWE | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
