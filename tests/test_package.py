"""Smoke tests for the initial package scaffold."""

import promptbench


def test_package_has_module_documentation() -> None:
    assert promptbench.__doc__
