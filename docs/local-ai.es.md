# IA local

La revisión con IA es opcional y **puede tardar varios minutos**. Solo corre en los perfiles
`full` y `vendor`, o en uno personalizado que incluya el módulo de IA, y usa un modelo que
corre **en tu equipo o en tu red**: nunca un servicio en la nube. Lo más sencillo es
[Ollama](https://ollama.com).

## Configurarla

1. Instala Ollama desde [ollama.com/download](https://ollama.com/download) y déjalo
   abierto. Escucha en `http://localhost:11434`.
2. Descarga un modelo y revisa su nombre exacto:

    ```bash
    ollama pull qwen2.5-coder:14b
    ollama list
    ```

3. Regístralo en **Ajustes → Revisión con IA**, o en `config.toml`:

    ```toml
    [llm]
    enabled = true
    active_destination = "laptop"

    [[llm.destinations]]
    name = "laptop"
    runtime = "ollama"
    url = "http://localhost:11434/v1"
    model_triage = "qwen2.5-coder:14b"       # valora si un hallazgo grave es real
    model_endpoints = "qwen2.5-coder:14b"    # revisa el control de acceso de cada endpoint
    model_summary = "qwen2.5-coder:14b"      # redacta el resumen ejecutivo
    model_sinks = "<sin definir>"            # opcional: revisa operaciones riesgosas; por defecto model_triage
    model_consensus = "<unset>"              # opcional: un segundo modelo para contrastar
    ```

4. Compruébala:

    ```bash
    uv run hdl llm
    ```

[LM Studio](https://lmstudio.ai) (`http://localhost:1234/v1`) y tu propio servidor vLLM
también funcionan. Puedes registrar varios destinos (cada uno un bloque `[[llm.destinations]]`)
y elegir uno por análisis con `hdl scan <carpeta> --profile full --ai <nombre>`.

## Qué modelo elegir

- Para valorar hallazgos y endpoints, un modelo *instruct* orientado a código (`coder` o
  `code` en el nombre).
- Para el resumen, cualquier modelo general con buen manejo del idioma: solo recibe cifras,
  nunca código.
- Un modelo de 7 a 8 mil millones de parámetros necesita cerca de 8 GB libres; uno de 14,
  unos 12 GB; uno de 30 o más, 24 GB o más.
- Un segundo modelo distinto en `model_consensus` hace que dos modelos valoren cada
  hallazgo. Tarda el doble.
- No sirven los modelos de *embeddings* ni los que terminan en `:cloud`.

## Modelos de razonamiento

Algunos modelos (por ejemplo las versiones "thinking" de Qwen) gastan cientos de tokens en
un razonamiento oculto antes de responder. Con las respuestas cortas que pide Heimdall, el
JSON puede quedar cortado o vacío y la respuesta cuenta como inutilizable. Por defecto
Heimdall le pide al servidor que no razone (`reasoning = "off"` en el destino, enviado como
`reasoning_effort: "none"`); si el servidor rechaza ese campo, se omite y no se vuelve a
intentar. Pon `reasoning = "on"` (o marca "Dejar que el modelo razone antes de responder" en
Ajustes) para que piense primero: las respuestas pueden mejorar, pero cada consulta tarda
mucho más. Cuando la mayoría de las respuestas son inutilizables, la corrida lo indica en
sus limitaciones.

## Privacidad (principio P3)

El destino debe ser `localhost`, `127.0.0.1` o `::1`, o cumplir las reglas de destino: el
host está en `allowed_hosts`, o es una IP privada o un dominio interno, y usa HTTPS. Los
modelos con el sufijo `:cloud` y las herramientas de IA en la nube se rechazan.

El código se envía al modelo sin comentarios y con los secretos enmascarados.

## Qué hace y qué no hace la IA

- **Operaciones riesgosas (T4).** Las reglas candidatas marcan operaciones peligrosas si les
  llega entrada del usuario (una consulta armada con texto, un comando, una ruta de archivo, una deserialización
  insegura, XML leído con entidades externas). Cubre código PHP, Python, JavaScript, C#,
  Kotlin, Swift y Dart. La IA comprueba, con la función completa y hasta dos de sus llamadores, si esa entrada
  realmente llega. Solo un riesgo alto con "alcanzable: sí" se convierte en un hallazgo de
  IA, siempre MEDIO, que no cuenta para el dictamen hasta que una persona lo confirme. Aquí
  la IA encuentra problemas que las reglas solas no reportan.
- **Endpoints (T2).** Revisa el control de acceso de cada endpoint con el código que lo
  decide: el manejador real (lo encuentra a partir de la ruta), la declaración de la ruta
  con su middleware y hasta tres funciones del proyecto que llama. Si no encuentra el
  manejador, guarda la revisión pero no crea sugerencia.
- **Hallazgos graves (T1).** Valora los críticos y altos, pero solo aquellos cuya regla no
  tiene ya confianza alta.
- **Resumen (T3).** Redacta el resumen ejecutivo con cifras agregadas, nunca con código.
- El presupuesto de la corrida se reparte en este orden: T4 (hasta el 60 %), luego T2 y luego
  T1. El tiempo total es el mismo que antes, pero se gasta donde se encuentran problemas
  nuevos.
- `model_sinks` define el modelo de T4 por destino; si no se define, se usa `model_triage`.
- Nunca recorre todo el repositorio.
- No cambia la severidad ni el estado de un hallazgo, aunque crea que es un falso positivo:
  sus resultados siempre aparecen marcados como sugerencia.
- Las sugerencias de la IA no cuentan para el dictamen del proveedor salvo que una persona
  las confirme.
- Las respuestas se guardan en caché: repetir un análisis sin cambios es casi inmediato.
