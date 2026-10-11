# Example Result

`zero-shot-result.json` is a PromptBench result produced by running `datasets/v1.jsonl` with `qwen2.5-coder:1.5b` through Ollama on October 4, 2026, using the current prompt and a maximum of 256 tokens per response.

That run passed 4 out of 5 cases (80%). All five cases generated executable tests. The `count-vowels` failure occurred because the model expected 6 vowels in `"Python Programming"`, while the code under test returns 4.

The result retains prompts, responses, latencies, and pytest output, as well as the dataset's exact content and SHA-256 hash and generation parameters, including `max_tokens`. A single run with a small model cannot establish that the prompt or model will behave the same way on later attempts.

To generate another result:

```powershell
.\.venv\Scripts\python.exe -m promptbench.cli run --dataset datasets/v1.jsonl --model qwen2.5-coder:1.5b --timeout 180 --max-tokens 256 --output examples/zero-shot-result.json
```
