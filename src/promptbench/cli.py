"""Interfaz de linea de comandos de PromptBench."""

import argparse
import json
from pathlib import Path
from typing import Any

from promptbench.domain import GenerationConfig
from promptbench.evaluation.runner import (
    CaseRunResult,
    ExperimentConfig,
    ExperimentResult,
    run_experiment,
)
from promptbench.prompts.zero_shot import ZeroShotPromptStrategy
from promptbench.providers.ollama import OllamaProvider


def main() -> None:
    """Punto de entrada instalado como el comando promptbench."""
    parser = argparse.ArgumentParser(
        prog="promptbench",
        description="Evalua prompts que generan tests pytest.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        description="Opciones disponibles",
    )

    run_parser = subparsers.add_parser("run", description="Comando para ejecutar las pruebas")
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--output", type=Path)
    run_parser.add_argument(
        "--max-tokens",
        type=int,
        default=256,
        help="Maximo de tokens generados por caso (por defecto: 256)",
    )
    run_parser.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="Tiempo maximo en segundos para cada generacion (por defecto: 180)",
    )

    args = parser.parse_args()

    if args.command == "run":
        config = ExperimentConfig(
            dataset_path=args.dataset,
            generation=GenerationConfig(
                model=args.model,
                timeout_seconds=args.timeout,
                max_tokens=args.max_tokens,
            ),
            strategy_name="zero-shot",
        )

        result = run_experiment(
            config=config,
            strategy=ZeroShotPromptStrategy(),
            provider=OllamaProvider(),
        )
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(_experiment_result_to_dict(result), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        print(f"Strategy: {result.strategy_name}")
        print(f"Model: {result.model}")
        print(f"Pass rate: {result.pass_rate:.0%}")
        print(f"Cases: {len(result.cases)}")
        if args.output is not None:
            print(f"Output: {args.output}")

        for case_result in result.cases:
            print()
            print(f"Case: {case_result.case_id}")
            print(f"Passed: {case_result.passed}")
            if case_result.error is not None:
                print(f"Status: {case_result.error}")
            print(f"Exit code: {case_result.execution.exit_code}")
            print(case_result.execution.stdout)
            print(case_result.execution.stderr)


def _experiment_result_to_dict(result: ExperimentResult) -> dict[str, Any]:
    return {
        "strategy_name": result.strategy_name,
        "model": result.model,
        "dataset": {
            "path": result.dataset_path,
            "sha256": result.dataset_sha256,
            "content": result.dataset_content,
        },
        "generation_config": {
            "model": result.generation_config.model,
            "temperature": result.generation_config.temperature,
            "timeout_seconds": result.generation_config.timeout_seconds,
            "max_tokens": result.generation_config.max_tokens,
        },
        "pass_rate": result.pass_rate,
        "cases": [_case_result_to_dict(case_result) for case_result in result.cases],
    }


def _case_result_to_dict(case_result: CaseRunResult) -> dict[str, Any]:
    return {
        "case_id": case_result.case_id,
        "passed": case_result.passed,
        "prompt": case_result.prompt,
        "error": case_result.error,
        "generated_text": (
            case_result.generation.text if case_result.generation is not None else None
        ),
        "generation_latency_ms": (
            case_result.generation.latency_ms if case_result.generation is not None else None
        ),
        "test_exit_code": case_result.execution.exit_code,
        "test_stdout": case_result.execution.stdout,
        "test_stderr": case_result.execution.stderr,
        "test_duration_ms": case_result.execution.duration_ms,
        "test_timed_out": case_result.execution.timed_out,
    }


if __name__ == "__main__":
    main()