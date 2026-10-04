"""Pruebas para la ejecucion controlada de tests generados."""

from textwrap import dedent

from promptbench.domain import EvaluationCase
from promptbench.evaluation.sandbox import normalize_generated_test_code, run_generated_tests


def make_case() -> EvaluationCase:
    return EvaluationCase(
        id="is-even",
        description="Comprueba pares e impares.",
        source_filename="number_utils.py",
        source_code="def is_even(value: int) -> bool:\n    return value % 2 == 0\n",
        test_filename="test_number_utils.py",
        tags=("math",),
    )


def test_run_generated_tests_returns_success_for_passing_tests() -> None:
    result = run_generated_tests(
        make_case(),
        dedent(
            """
            from number_utils import is_even

            def test_even_number():
                assert is_even(2) is True
            """
        ).strip(),
    )

    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.duration_ms >= 0


def test_run_generated_tests_returns_failure_for_failing_tests() -> None:
    result = run_generated_tests(
        make_case(),
        dedent(
            """
            from number_utils import is_even

            def test_wrong_expectation():
                assert is_even(2) is False
            """
        ).strip(),
    )

    assert result.exit_code != 0
    assert result.timed_out is False
    assert "failed" in result.stdout.lower()


def test_run_generated_tests_explains_empty_model_response() -> None:
    result = run_generated_tests(make_case(), "  ")

    assert result.exit_code != 0
    assert "respuesta vacia" in result.stdout.lower()


def test_run_generated_tests_explains_invalid_python() -> None:
    result = run_generated_tests(make_case(), "def test_broken(:\n    pass")

    assert result.exit_code != 0
    assert "codigo generado invalido" in result.stdout.lower()


def test_run_generated_tests_explains_missing_test_function() -> None:
    result = run_generated_tests(make_case(), "value = 1")

    assert result.exit_code != 0
    assert "no genero tests" in result.stdout.lower()


def test_normalize_generated_test_code_removes_markdown_fence() -> None:
    generated_code = dedent(
        """
        ```python
        from number_utils import is_even

        def test_even_number():
            assert is_even(2) is True
        ```
        """
    )

    normalized = normalize_generated_test_code(generated_code)

    assert normalized.startswith("from number_utils import is_even")
    assert "```" not in normalized


def test_run_generated_tests_accepts_markdown_fenced_code() -> None:
    result = run_generated_tests(
        make_case(),
        dedent(
            """
            ```python
            from number_utils import is_even

            def test_even_number():
                assert is_even(2) is True
            ```
            """
        ),
    )

    assert result.exit_code == 0
    assert result.timed_out is False