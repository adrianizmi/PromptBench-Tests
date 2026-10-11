# PromptBench Tests

A local tool for evaluating prompts that generate `pytest` tests from JSONL cases.

The project measures the functional quality of generated tests: it loads a dataset, builds a zero-shot prompt, queries a local model through Ollama, runs the response with `pytest`, and calculates the pass rate.

## Scope

The current version provides an end-to-end, executable zero-shot workflow. It includes dataset validation, strategy and provider contracts, an Ollama adapter, temporary test execution, reproducible JSON results, and unit tests. Few-shot prompting and strategy comparisons are outside the scope of this version.

Each JSON result records:

- The exact dataset content, path, and SHA-256 hash.
- The model, strategy, temperature, timeout, and maximum number of tokens.
- The prompt, response, latency, and `pytest` output for each case.
- Generation errors, empty responses, invalid Python, and cases without tests.

## Requirements

- Python 3.12.
- Docker Desktop to run Ollama through Compose.
- An NVIDIA GPU compatible with Docker for GPU acceleration. The service can also run on CPU by removing the device reservation from `compose.yaml`.

The model used to generate the example artifact is `qwen2.5-coder:1.5b`.

## Installation

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Local Ollama

Start the service:

```powershell
docker compose up -d
```

Download the example model:

```powershell
docker compose exec ollama ollama pull qwen2.5-coder:1.5b
```

Check the service at `http://localhost:11434/api/tags`. To stop it while retaining downloaded models:

```powershell
docker compose stop
```

Compose pins the service image to `ollama/ollama:0.35.1` to avoid unexpected changes from the `latest` tag.

## Usage

Run the experiment and save an artifact:

```powershell
.\.venv\Scripts\python.exe -m promptbench.cli run --dataset datasets/v1.jsonl --model qwen2.5-coder:1.5b --timeout 180 --max-tokens 256 --output examples/zero-shot-result.json
```

The command prints a summary and the result for every case. If generation fails for a case, it records the error, retains completed cases, and continues with the remaining ones. The pass rate counts only passing cases.

The [example artifact](examples/zero-shot-result.json) records one run across five cases. In that run, four cases passed (80%); `count-vowels` failed because the model proposed an incorrect expectation. It does not guarantee future results. Read [the artifact context](examples/README.md) before interpreting it.

## Tests and Quality

Integration tests are excluded by default so the suite does not depend on Docker:

```powershell
.\.venv\Scripts\pytest.exe
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src
```

To run the Ollama integration test:

```powershell
docker compose up -d
.\.venv\Scripts\pytest.exe -m integration
```

## Dataset

Each line in `datasets/v1.jsonl` represents a case with `id`, `description`, `source_filename`, `source_code`, `test_filename`, and `tags`. Cases must be synthetic, small, and deterministic. Do not include secrets, personal data, or corporate code.

## Architecture

```text
src/promptbench/
  domain.py                 # Shared models
  datasets.py               # JSONL loading and validation
  prompts/base.py           # PromptStrategy contract
  prompts/zero_shot.py      # Zero-shot strategy
  providers/base.py         # LLMProvider contract
  providers/ollama.py       # Ollama HTTP adapter
  evaluation/sandbox.py     # Temporary test execution
  evaluation/runner.py      # Orchestration and reproducible results
  evaluation/metrics.py     # Metrics
  cli.py                    # Command-line interface
```

The runner relies on contracts to separate orchestration from the model provider and prompting strategy.

## Security and Limitations

The temporary directory prevents repository clutter but does not isolate hostile code. Generated tests run as local processes and have a timeout; this is not a security boundary. Use trusted datasets only. Running untrusted input requires real isolation, such as unprivileged ephemeral containers or a disposable machine.

The pass rate measures whether generated tests pass against the supplied code. It does not measure coverage or guarantee that tests are complete or correct.
