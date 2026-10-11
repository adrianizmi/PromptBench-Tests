"""Orchestration for an experiment over a complete dataset."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from promptbench.datasets import load_cases
from promptbench.domain import GeneratedResponse, GenerationConfig
from promptbench.evaluation.metrics import calculate_pass_rate
from promptbench.evaluation.sandbox import TestExecution, run_generated_tests
from promptbench.prompts.base import PromptStrategy
from promptbench.providers.base import LLMProvider


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Reproducible experiment configuration."""

    dataset_path: Path
    generation: GenerationConfig
    strategy_name: str


@dataclass(frozen=True, slots=True)
class CaseRunResult:
    """Complete result of running one dataset case."""

    case_id: str
    prompt: str
    generation: GeneratedResponse | None
    execution: TestExecution
    error: str | None = None

    @property
    def passed(self) -> bool:
        """Whether generated tests passed without timing out."""
        return (
            self.error is None
            and self.generation is not None
            and self.execution.exit_code == 0
            and not self.execution.timed_out
        )


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Aggregated result of an experiment."""

    strategy_name: str
    model: str
    dataset_path: str
    dataset_sha256: str
    dataset_content: str
    generation_config: GenerationConfig
    cases: list[CaseRunResult]
    pass_rate: float


def run_experiment(
    config: ExperimentConfig,
    strategy: PromptStrategy,
    provider: LLMProvider,
) -> ExperimentResult:
    """Coordinate loading, prompting, generation, execution, and metrics."""
    dataset_content = config.dataset_path.read_text(encoding="utf-8")
    dataset_hash = sha256(dataset_content.encode("utf-8")).hexdigest()
    cases = load_cases(config.dataset_path)
    results: list[CaseRunResult] = []

    for case in cases:
        prompt = strategy.build(case)
        try:
            generation = provider.generate(prompt, config.generation)
        except Exception as error:  # noqa: BLE001 - provider failures become case results.
            if isinstance(error, TimeoutError) or "timeout" in type(error).__name__.lower():
                message = "Timed out while requesting a generation from the provider."
            else:
                detail = str(error).strip()
                message = f"Provider failed ({type(error).__name__})"
                if detail:
                    message += f": {detail}"

            results.append(
                CaseRunResult(
                    case_id=case.id,
                    prompt=prompt,
                    generation=None,
                    execution=TestExecution(
                        exit_code=-1,
                        stdout="",
                        stderr=message,
                        duration_ms=0.0,
                        timed_out=False,
                    ),
                    error=message,
                )
            )
            continue

        execution = run_generated_tests(case, generation.text)

        results.append(
            CaseRunResult(
                case_id=case.id,
                prompt=prompt,
                generation=generation,
                execution=execution,
                error=None if execution.exit_code == 0 else _execution_error(execution),
            )
        )

    passing_cases = sum(result.passed for result in results)
    pass_rate = calculate_pass_rate(
        total_cases=len(results),
        passing_cases=passing_cases,
    )

    return ExperimentResult(
        strategy_name=config.strategy_name,
        model=config.generation.model,
        dataset_path=str(config.dataset_path),
        dataset_sha256=dataset_hash,
        dataset_content=dataset_content,
        generation_config=config.generation,
        cases=results,
        pass_rate=pass_rate,
    )


def _execution_error(execution: TestExecution) -> str:
    if execution.timed_out:
        return "Generated tests exceeded the time limit."
    diagnostic = execution.stdout or execution.stderr
    if "no tests were generated" in diagnostic.lower():
        return "The model did not generate an executable test function."
    if "invalid generated code" in diagnostic.lower():
        return "The model generated invalid Python code."
    return "Generated tests did not pass."
