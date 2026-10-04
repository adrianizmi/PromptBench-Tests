"""Carga y validacion de datasets de evaluacion."""

import json
from pathlib import Path
from typing import Any, cast

from promptbench.domain import EvaluationCase

REQUIRED_FIELDS = (
    "id",
    "description",
    "source_filename",
    "source_code",
    "test_filename",
    "tags",
)


def load_cases(dataset_path: Path) -> list[EvaluationCase]:
    """Carga casos de evaluacion desde un fichero JSONL."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"No existe el dataset: {dataset_path}")
    if not dataset_path.is_file():
        raise ValueError(f"La ruta no es un fichero: {dataset_path}")

    cases: list[EvaluationCase] = []
    with dataset_path.open(encoding="utf-8") as dataset_file:
        for line_number, line in enumerate(dataset_file, start=1):
            if not line.strip():
                continue

            try:
                raw_case = json.loads(line)
                cases.append(_parse_case(raw_case, line_number))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Error de formato JSON en la linea {line_number}: {error}"
                ) from error

    return cases


def _parse_case(raw_case: Any, line_number: int) -> EvaluationCase:
    if not isinstance(raw_case, dict):
        raise TypeError(f"El objeto de la linea {line_number} debe ser un JSON object.")

    case_data = cast(dict[str, Any], raw_case)
    case_id = case_data.get("id", "<sin id>")
    for field in REQUIRED_FIELDS:
        if field not in case_data:
            raise ValueError(
                f"Falta el campo {field!r} en el objeto de la linea {line_number}, "
                f"caso {case_id}"
            )

    tags = case_data["tags"]
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError(
            f"El campo 'tags' debe ser una lista de strings en la linea {line_number}, "
            f"caso {case_id}"
        )

    try:
        return EvaluationCase(
            id=_require_str(case_data, "id", line_number, case_id),
            description=_require_str(case_data, "description", line_number, case_id),
            source_filename=_require_str(case_data, "source_filename", line_number, case_id),
            source_code=_require_str(case_data, "source_code", line_number, case_id),
            test_filename=_require_str(case_data, "test_filename", line_number, case_id),
            tags=tuple(tags),
        )
    except ValueError as error:
        raise ValueError(
            f"Caso invalido en la linea {line_number}, caso {case_id}: {error}"
        ) from error


def _require_str(raw_case: dict[str, Any], field: str, line_number: int, case_id: object) -> str:
    value = raw_case[field]
    if not isinstance(value, str):
        raise TypeError(
            f"El campo {field!r} debe ser un string en la linea {line_number}, caso {case_id}"
        )
    return value
