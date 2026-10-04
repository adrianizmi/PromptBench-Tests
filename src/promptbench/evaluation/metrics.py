"""Metricas derivadas de las ejecuciones de un experimento."""


def calculate_pass_rate(total_cases: int, passing_cases: int) -> float:
    """Calcula la proporcion de casos que pasan."""

    if total_cases == 0:
        raise ValueError(f"No hay pruebas. Los casos totales son: {total_cases}")

    return passing_cases / total_cases
