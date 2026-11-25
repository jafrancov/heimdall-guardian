# Contribuir

Gracias por querer mejorar Heimdall Guardian. La guía completa es
[CONTRIBUTING.es.md](https://github.com/jafrancov/heimdall-guardian/blob/main/CONTRIBUTING.es.md)
en el repositorio. En resumen:

- Lee primero los seis principios no negociables: un cambio que viole uno se rechaza.
- Una regla nueva es un archivo YAML en `rules/heimdall/<stack>/`, con textos en inglés y en
  español, fixtures positivos y negativos y un conteo esperado exacto.
- El texto visible va en los dos catálogos de idioma.
- Deja `pre-commit run --all-files` en verde antes de enviar tu cambio.
- Agrégate a
  [CONTRIBUTORS.es.md](https://github.com/jafrancov/heimdall-guardian/blob/main/CONTRIBUTORS.es.md)
  en el mismo pull request.

## Construir este sitio

La documentación usa MkDocs Material. Sus herramientas viven en el grupo de dependencias
`docs`:

```bash
make docs         # regenera las páginas generadas y construye el sitio en modo estricto
make docs-serve   # vista previa en vivo
```

El catálogo de reglas, la página de OWASP, la de stacks y la referencia de la línea de
comandos las genera `tools/build_rule_docs.py` a partir de los archivos de reglas y del
código. No las edites a mano: una prueba falla si las páginas versionadas están desactualizadas.

Para reportar una vulnerabilidad, sigue
[SECURITY.es.md](https://github.com/jafrancov/heimdall-guardian/blob/main/SECURITY.es.md).
