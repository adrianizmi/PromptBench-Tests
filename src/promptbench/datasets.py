"""Loading and validation for evaluation datasets."""

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
    """Load evaluation cases from a JSONL file."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset does not exist: {dataset_path}")
    if not dataset_path.is_file():
        raise ValueError(f"Path is not a file: {dataset_path}")

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
                    f"Invalid JSON format on line {line_number}: {error}"
                ) from error

    return cases


def _parse_case(raw_case: Any, line_number: int) -> EvaluationCase:
    if not isinstance(raw_case, dict):
        raise TypeError(f"Object on line {line_number} must be a JSON object.")

    case_data = cast(dict[str, Any], raw_case)
    case_id = case_data.get("id", "<missing id>")
    for field in REQUIRED_FIELDS:
        if field not in case_data:
            raise ValueError(
                f"Missing field {field!r} in object on line {line_number}, "
                f"case {case_id}"
            )

    tags = case_data["tags"]
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError(
            f"Field 'tags' must be a list of strings on line {line_number}, "
            f"case {case_id}"
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
            f"Invalid case on line {line_number}, case {case_id}: {error}"
        ) from error


def _require_str(raw_case: dict[str, Any], field: str, line_number: int, case_id: object) -> str:
    value = raw_case[field]
    if not isinstance(value, str):
        raise TypeError(
            f"Field {field!r} must be a string on line {line_number}, case {case_id}"
        )
    return value
