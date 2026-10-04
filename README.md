# PromptBench Tests

Herramienta local para evaluar prompts que generan tests `pytest` a partir de casos JSONL.

El proyecto compara la calidad funcional de los tests generados: carga un dataset, crea un prompt zero-shot, consulta un modelo local mediante Ollama, ejecuta la respuesta con `pytest` y calcula el porcentaje de casos superados.

## Alcance

La version actual ofrece un flujo zero-shot ejecutable de principio a fin. Incluye validacion de datasets, contratos para estrategias y proveedores, adaptador de Ollama, ejecucion temporal de tests, resultados JSON reproducibles y pruebas unitarias. Few-shot y la comparacion entre estrategias quedan fuera del alcance de esta version.

Cada resultado JSON conserva:

- El contenido exacto del dataset, su ruta y su hash SHA-256.
- Modelo, estrategia, temperatura, timeout y maximo de tokens.
- Prompt, respuesta, latencia y salida de `pytest` por caso.
- Errores de generacion, respuestas vacias, codigo invalido y casos sin tests.

## Requisitos

- Python 3.12.
- Docker Desktop para ejecutar Ollama mediante Compose.
- GPU NVIDIA compatible con Docker si se quiere usar aceleracion GPU; el servicio tambien se puede ejecutar en CPU quitando la reserva de dispositivo de `compose.yaml`.

El modelo utilizado para generar el artefacto de ejemplo es `qwen2.5-coder:1.5b`.

## Instalacion

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Ollama Local

Inicia el servicio:

```powershell
docker compose up -d
```

Descarga el modelo de ejemplo:

```powershell
docker compose exec ollama ollama pull qwen2.5-coder:1.5b
```

Comprueba el servicio en `http://localhost:11434/api/tags`. Para detenerlo sin borrar los modelos descargados:

```powershell
docker compose stop
```

Compose fija la imagen del servicio en `ollama/ollama:0.35.1` para evitar cambios inesperados por el tag `latest`.

## Uso

Ejecuta el experimento y guarda un artefacto:

```powershell
.\.venv\Scripts\python.exe -m promptbench.cli run --dataset datasets/v1.jsonl --model qwen2.5-coder:1.5b --timeout 180 --max-tokens 256 --output examples/zero-shot-result.json
```

El comando muestra un resumen y el resultado de cada caso. Si falla la generacion para un caso, guarda el error, mantiene los casos ya procesados y continua con los siguientes. El porcentaje solo cuenta los casos que pasaron.

El [artefacto de ejemplo](examples/zero-shot-result.json) registra una ejecucion concreta sobre cinco casos. En esa ejecucion, cuatro pasaron (80%); `count-vowels` fallo porque el modelo propuso una expectativa incorrecta. No es una garantia de resultados futuros. Consulta [el contexto del artefacto](examples/README.md) antes de interpretarlo.

## Tests Y Calidad

Los tests de integracion se excluyen por defecto para que la suite no dependa de Docker:

```powershell
.\.venv\Scripts\pytest.exe
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src
```

Para ejecutar la prueba de integracion con Ollama:

```powershell
docker compose up -d
.\.venv\Scripts\pytest.exe -m integration
```

## Dataset

Cada linea de `datasets/v1.jsonl` representa un caso con `id`, `description`, `source_filename`, `source_code`, `test_filename` y `tags`. Los casos deben ser sinteticos, pequenos y deterministas. No incluyas secretos, datos personales ni codigo corporativo.

## Arquitectura

```text
src/promptbench/
  domain.py                 # Modelos compartidos
  datasets.py               # Carga y validacion JSONL
  prompts/base.py           # Contrato PromptStrategy
  prompts/zero_shot.py      # Estrategia zero-shot
  providers/base.py         # Contrato LLMProvider
  providers/ollama.py       # Adaptador HTTP de Ollama
  evaluation/sandbox.py     # Ejecucion temporal de tests
  evaluation/runner.py      # Orquestacion y resultados reproducibles
  evaluation/metrics.py     # Metricas
  cli.py                    # Interfaz de linea de comandos
```

El runner depende de contratos para separar la orquestacion del proveedor de modelos y de la estrategia de prompting.

## Seguridad Y Limitaciones

El directorio temporal evita ensuciar el repositorio, pero no aisla codigo hostil. Los tests generados se ejecutan como procesos locales y tienen un timeout; esto no es una frontera de seguridad. Usa unicamente datasets de confianza. Ejecutar entradas no confiables requeriria aislamiento real, por ejemplo contenedores efimeros sin privilegios o una maquina desechable.

El pass rate mide si los tests generados pasan contra el codigo proporcionado; no mide la cobertura ni garantiza que los tests sean completos o correctos.
