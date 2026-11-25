# NET-CONF-002: web.config inseguro (customErrors, debug, validateRequest)

[Volver al catálogo de reglas](index.es.md)

## Qué detecta

Configuración de ASP.NET insegura para producción: errores detallados visibles, compilación en modo debug o validación de peticiones desactivada.

## Cómo corregirlo

Usar customErrors mode="RemoteOnly" u "On", compilation debug="false" y mantener validateRequest activo.

## Por qué importa

Esta regla corresponde a [CWE-16](https://cwe.mitre.org/data/definitions/16.html) y a la categoría A02:2025 Configuración de seguridad incorrecta del OWASP Top 10:2025.

## Cómo verificarlo

Abre el archivo de configuración del entorno de producción y compare el valor con el recomendado: modo de depuración apagado, orígenes acotados y sin valores de prueba.

## Datos

| | |
|---|---|
| Severidad | MEDIA |
| Confianza | ALTA |
| Categoría | CONFIGURACION |
| Stack | .NET |
| Lenguajes | `regex` |
| CWE | [CWE-16](https://cwe.mitre.org/data/definitions/16.html) |
| OWASP | A02:2025 Configuración de seguridad incorrecta |
