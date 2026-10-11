"""Metrics derived from experiment runs."""


def calculate_pass_rate(total_cases: int, passing_cases: int) -> float:
    """Calculate the proportion of passing cases."""

    if total_cases == 0:
        raise ValueError(f"There are no tests. Total cases: {total_cases}")

    return passing_cases / total_cases
