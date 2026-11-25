# Proyecto de demostración: Corner Shop

Una aplicación pequeña y **vulnerable a propósito** para mostrar lo que reporta Heimdall.
Mezcla cuatro stacks, como muchas entregas reales:

- `backend/`: un servicio Django (SQL armado con f-strings, un comando con `shell=True`,
  vistas sin autenticación, `DEBUG = True`, subida de archivos sin restricción) con un
  `requirements.txt` viejo y un `Dockerfile` con malas prácticas.
- `api/`: un servicio Express (inyección NoSQL, CORS permisivo, secreto de sesión débil,
  JWT sin verificar, path traversal, un endpoint de borrado sin protección) con su
  `package-lock.json`.
- `mobile/`: una app Flutter (tokens en `SharedPreferences`, direcciones `http://`, acepta
  cualquier certificado, un manifiesto de Android permisivo) con su `pubspec.lock`.
- `.env.example`: secretos inventados.

## Lee esto primero

- **No la despliegues ni la ejecutes.** Cada debilidad está puesta a propósito y las
  dependencias viejas tienen vulnerabilidades conocidas.
- Todas las credenciales son inventadas. Ninguna sirve en un servicio real ni usa el
  formato de un proveedor real; solo parecen secretos para los patrones genéricos.
- Las herramientas de calidad (ruff, mypy, pytest, pre-commit) omiten esta carpeta.

## Analízala

```bash
uv run hdl scan examples/demo-project --profile standard --output demo.html
```

O abre la carpeta desde la aplicación de escritorio (`uv run hdl ui`). Para los hallazgos de
dependencias necesitas las bases de vulnerabilidades (`uv run hdl databases --update`,
cerca de 1.4 GB); sin ellas el resto del resultado es el mismo. Los reportes no se pueden
guardar dentro de la carpeta analizada, escríbelos en otro lugar.

Deberías ver hallazgos en todas las severidades, varias categorías de OWASP Top 10:2025, el
inventario de endpoints con y sin autenticación y dependencias vulnerables.
