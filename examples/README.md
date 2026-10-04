# Ejemplo de resultado

`zero-shot-result.json` es la salida de PromptBench al ejecutar `datasets/v1.jsonl` con `qwen2.5-coder:1.5b` mediante Ollama el 4 de octubre de 2026, usando el prompt actual y un maximo de 256 tokens por respuesta.

En esa ejecucion pasaron 4 de 5 casos (80%). Los cinco casos generaron tests ejecutables. El fallo de `count-vowels` se debe a que el modelo esperaba 6 vocales en `"Python Programming"`, mientras que el codigo bajo prueba devuelve 4.

El resultado conserva los prompts, respuestas, latencias y salida de pytest, ademas del contenido exacto y hash SHA-256 del dataset y los parametros de generacion, incluido `max_tokens`. Una unica ejecucion con un modelo pequeno no permite concluir que el prompt o el modelo se comportaran igual en otros intentos.

Para generar otro resultado:

```powershell
.\.venv\Scripts\python.exe -m promptbench.cli run --dataset datasets/v1.jsonl --model qwen2.5-coder:1.5b --timeout 180 --max-tokens 256 --output examples/zero-shot-result.json
```
