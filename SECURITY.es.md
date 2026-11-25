# Seguridad

[Read in English → SECURITY.md](SECURITY.md)

## Reportar una vulnerabilidad en Heimdall Guardian

Si encuentras una falla de seguridad en esta herramienta, no abras un issue público.
Usa **Security → Report a vulnerability** en el repositorio de GitHub (reporte privado).
Incluye qué versión usas, cómo reproducirla y qué impacto ves.

Interesa en particular cualquier forma de que el código analizado:

- logre ejecutarse o lanzar un programa durante el análisis;
- escriba dentro o fuera de la carpeta analizada;
- oculte hallazgos mediante archivos de configuración o comentarios;
- haga salir código, secretos o inventarios de la red local;
- manipule al modelo de IA para cambiar un resultado;
- aparezca sin enmascarar (un secreto) en un reporte.

## Alcance de la herramienta

Heimdall Guardian hace análisis estático. No sustituye pruebas de penetración ni la
revisión manual de la lógica de negocio. Un resultado sin hallazgos no significa que el
código sea seguro.
