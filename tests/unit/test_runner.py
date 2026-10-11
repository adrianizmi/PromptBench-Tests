"""Tests for experiment orchestration."""

from pathlib import Path

from promptbench.domain import GeneratedResponse, GenerationConfig
from promptbench.evaluation.runner import ExperimentConfig, run_experiment
from promptbench.prompts.zero_shot import ZeroShotPromptStrategy


class FakeProvider:
    """Deterministic provider for testing the runner without calling a real LLM."""

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        return GeneratedResponse(
            text="""from number_utils import is_even


def test_even_number():
    assert is_even(2) is True
""",
            latency_ms=1.0,
        )


class FailOnSecondProvider(FakeProvider):
    """Simulate a timeout after completing one case."""

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        self.calls += 1
        if self.calls == 2:
            raise TimeoutError("test timeout")
        return super().generate(prompt, config)


def test_run_experiment_generates_and_executes_tests(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(
        '{"id":"is-even","description":"Check even and odd values.",'
        '"source_filename":"number_utils.py",'
        '"source_code":"def is_even(value: int) -> bool:\\n    return value % 2 == 0\\n",'
        '"test_filename":"test_number_utils.py",'
        '"tags":["math"]}\n',
        encoding="utf-8",
    )
    config = ExperimentConfig(
        dataset_path=dataset_path,
        generation=GenerationConfig(model="fake-model"),
        strategy_name="zero-shot",
    )

    result = run_experiment(
        config=config,
        strategy=ZeroShotPromptStrategy(),
        provider=FakeProvider(),
    )

    assert result.strategy_name == "zero-shot"
    assert result.model == "fake-model"
    assert result.pass_rate == 1.0
    assert len(result.cases) == 1
    assert result.cases[0].case_id == "is-even"
    assert result.cases[0].passed is True


def test_run_experiment_keeps_completed_cases_after_provider_timeout(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(
        '{"id":"first","description":"desc","source_filename":"number_utils.py",'
        '"source_code":"def is_even(value): return value % 2 == 0", '
        '"test_filename":"test_number_utils.py", "tags":[]}\n'
        '{"id":"second","description":"desc","source_filename":"number_utils.py",'
        '"source_code":"def is_even(value): return value % 2 == 0", '
        '"test_filename":"test_number_utils.py", "tags":[]}\n',
        encoding="utf-8",
    )
    config = ExperimentConfig(
        dataset_path=dataset_path,
        generation=GenerationConfig(model="fake-model"),
        strategy_name="zero-shot",
    )

    result = run_experiment(config, ZeroShotPromptStrategy(), FailOnSecondProvider())

    assert len(result.cases) == 2
    assert result.cases[0].passed is True
    assert result.cases[1].passed is False
    assert result.cases[1].generation is None
    assert "timed out" in (result.cases[1].error or "").lower()
    assert result.cases[1].execution.timed_out is False
    assert result.pass_rate == 0.5
    assert result.dataset_content == dataset_path.read_text(encoding="utf-8")
    assert result.dataset_sha256
