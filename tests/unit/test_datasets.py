"""Tests for JSONL dataset loading."""

import json
from pathlib import Path

import pytest

from promptbench.datasets import load_cases
from promptbench.domain import EvaluationCase


def test_load_cases_reads_jsonl_into_domain_objects(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(
        '{"id":"case-1","description":"desc","source_filename":"code.py","source_code":"def foo():\\n    return 1\\n","test_filename":"test_code.py","tags":["basic","unit"]}\n'
        '{"id":"case-2","description":"desc 2","source_filename":"other.py","source_code":"def bar():\\n    return 2\\n","test_filename":"test_other.py","tags":["edge"]}\n',
        encoding="utf-8",
    )

    cases = load_cases(dataset_path)

    assert len(cases) == 2
    assert isinstance(cases[0], EvaluationCase)
    assert cases[0].id == "case-1"
    assert cases[0].source_code == "def foo():\n    return 1\n"
    assert cases[0].tags == ("basic", "unit")


def test_load_cases_reports_the_line_of_invalid_json(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(
        '{"id":"case-1","description":"desc","source_filename":"code.py","source_code":"def foo():\\n    return 1\\n","test_filename":"test_code.py","tags":["basic","unit"]}\n'
        '{invalid json}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as error:
        load_cases(dataset_path)

    assert "line 2" in str(error.value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_filename", "../outside.py"),
        ("source_filename", r"..\outside.py"),
        ("test_filename", "C:\\outside.py"),
        ("test_filename", "code.py"),
    ],
)
def test_load_cases_rejects_unsafe_or_duplicate_filenames(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    case_data = {
        "id": "case-1",
        "description": "desc",
        "source_filename": "code.py",
        "source_code": "def foo(): return 1",
        "test_filename": "test_code.py",
        "tags": ["basic"],
    }
    case_data[field] = value
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(json.dumps(case_data), encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        load_cases(dataset_path)
