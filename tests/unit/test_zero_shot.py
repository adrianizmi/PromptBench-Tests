"""Tests for the zero-shot strategy."""

from promptbench.domain import EvaluationCase
from promptbench.prompts.zero_shot import ZeroShotPromptStrategy, build_zero_shot_prompt


def test_zero_shot_prompt_contains_the_case_context() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Check even and odd values.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    prompt = build_zero_shot_prompt(case)

    assert "Check even and odd values." in prompt
    assert "number_utils.py" in prompt
    assert "number_utils" in prompt
    assert "def is_even" in prompt
    assert "test_number_utils.py" in prompt


def test_zero_shot_prompt_requires_code_only() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Check even and odd values.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    prompt = build_zero_shot_prompt(case)

    assert "valid Python code only" in prompt
    assert "Do not include Markdown" in prompt
    assert "Do not include explanations" in prompt
    assert "Include explicit imports" in prompt
    assert "from number_utils import <required_functions>" in prompt


def test_zero_shot_strategy_builds_prompt() -> None:
    case = EvaluationCase(
        id="is-even",
        description="Check even and odd values.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )

    strategy = ZeroShotPromptStrategy()

    prompt = strategy.build(case)

    assert "Check even and odd values." in prompt
    assert "def is_even" in prompt
