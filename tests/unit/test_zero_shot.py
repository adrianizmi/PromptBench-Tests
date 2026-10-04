"""Pruebas para la estrategia zero-shot."""

from promptbench.domain import EvaluationCase
from promptbench.prompts.zero_shot import ZeroShotPromptStrategy, build_zero_shot_prompt


def test_zero_shot_prompt_contains_the_case_context() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Comprueba pares e impares.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    prompt = build_zero_shot_prompt(case)

    assert "Comprueba pares e impares." in prompt
    assert "number_utils.py" in prompt
    assert "number_utils" in prompt
    assert "def is_even" in prompt
    assert "test_number_utils.py" in prompt


def test_zero_shot_prompt_requires_code_only() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Comprueba pares e impares.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    prompt = build_zero_shot_prompt(case)

    assert "codigo Python valido" in prompt
    assert "No incluyas Markdown" in prompt
    assert "No incluyas explicaciones" in prompt
    assert "Incluye los imports explicitos" in prompt
    assert "from number_utils import <funciones_necesarias>" in prompt


def test_zero_shot_strategy_builds_prompt() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Comprueba pares e impares.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    strategy = ZeroShotPromptStrategy()

    prompt = strategy.build(case)

    assert "Comprueba pares e impares." in prompt
    assert "def is_even" in prompt
