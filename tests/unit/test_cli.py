"""Pruebas para helpers de serializacion de la CLI."""

from promptbench.cli import _experiment_result_to_dict
from promptbench.domain import GeneratedResponse, GenerationConfig
from promptbench.evaluation.runner import CaseRunResult, ExperimentResult
from promptbench.evaluation.sandbox import TestExecution as ExecutionResult


def test_experiment_result_to_dict_keeps_reproducible_fields() -> None:
    result = ExperimentResult(
        strategy_name="zero-shot",
        model="fake-model",
        dataset_path="datasets/v1.jsonl",
        dataset_sha256="abc123",
        dataset_content='{"id":"is-even"}',
        generation_config=GenerationConfig(
            model="fake-model",
            temperature=0.2,
            timeout_seconds=30,
            max_tokens=512,
        ),
        pass_rate=1.0,
        cases=[
            CaseRunResult(
                case_id="is-even",
                prompt="prompt",
                generation=GeneratedResponse(text="generated", latency_ms=12.5),
                execution=ExecutionResult(
                    exit_code=0,
                    stdout="1 passed",
                    stderr="",
                    duration_ms=34.0,
                    timed_out=False,
                ),
            )
        ],
    )

    payload = _experiment_result_to_dict(result)

    assert payload["strategy_name"] == "zero-shot"
    assert payload["model"] == "fake-model"
    assert payload["dataset"]["path"] == "datasets/v1.jsonl"
    assert payload["dataset"]["sha256"] == "abc123"
    assert payload["dataset"]["content"] == '{"id":"is-even"}'
    assert payload["generation_config"]["max_tokens"] == 512
    assert payload["pass_rate"] == 1.0
    assert payload["cases"][0]["case_id"] == "is-even"
    assert payload["cases"][0]["passed"] is True
    assert payload["cases"][0]["generated_text"] == "generated"
    assert payload["cases"][0]["test_stdout"] == "1 passed"
