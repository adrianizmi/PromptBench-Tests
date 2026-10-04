"""Ejecucion acotada de tests generados para datasets de confianza."""

import ast
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from promptbench.domain import EvaluationCase


@dataclass(frozen=True, slots=True)
class TestExecution:
    """Resultado de ejecutar pytest sobre un unico caso generado."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool


def normalize_generated_test_code(generated_test_code: str) -> str:
    """Elimina fences Markdown habituales sin modificar el codigo interno."""
    code = generated_test_code.strip()

    if code.startswith("```python"):
        code = code.removeprefix("```python").strip()
    elif code.startswith("```"):
        code = code.removeprefix("```").strip()

    if code.endswith("```"):
        code = code.removesuffix("```").strip()

    return code


def run_generated_tests(case: EvaluationCase, generated_test_code: str) -> TestExecution:
    """Escribe archivos temporales y ejecuta pytest.

    Seguridad: nunca uses shell=True ni ejecutes casos no confiables. Esta version
    evalua solo ejemplos sinteticos del repositorio; aislar codigo hostil exige
    contenedores o una maquina dedicada, no solo un directorio temporal.
    """

    normalized_code = normalize_generated_test_code(generated_test_code)
    if not normalized_code:
        return _invalid_test_result("El modelo no genero tests (respuesta vacia).")

    try:
        syntax_tree = ast.parse(normalized_code)
    except SyntaxError as error:
        return _invalid_test_result(
            f"Codigo generado invalido: error de sintaxis en linea {error.lineno}: {error.msg}"
        )

    if not _contains_test_function(syntax_tree):
        return _invalid_test_result("El modelo no genero tests: falta una funcion test_.")

    with TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)

        source_path = work_dir / case.source_filename
        test_path = work_dir / case.test_filename

        source_path.write_text(case.source_code, encoding="utf-8")
        test_path.write_text(normalized_code, encoding="utf-8")

        start = time.perf_counter()

        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            duration_ms = (time.perf_counter() - start) * 1000

            return TestExecution(
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as error:
            duration_ms = (time.perf_counter() - start) * 1000

            return TestExecution(
                exit_code=-1,
                stdout=_output_to_text(error.stdout),
                stderr=_output_to_text(error.stderr),
                duration_ms=duration_ms,
                timed_out=True,
            )


def _output_to_text(output: str | bytes | None) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode(errors="replace")
    return output


def _contains_test_function(syntax_tree: ast.Module) -> bool:
    for node in syntax_tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            return True
        if (
            isinstance(node, ast.ClassDef)
            and node.name.startswith("Test")
            and any(
                isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                and member.name.startswith("test_")
                for member in node.body
            )
        ):
            return True
    return False


def _invalid_test_result(message: str) -> TestExecution:
    return TestExecution(
        exit_code=2,
        stdout=message,
        stderr="",
        duration_ms=0.0,
        timed_out=False,
    )
