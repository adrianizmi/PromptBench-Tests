"""Modelos de datos que viajan entre las capas del experimento."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    """Representa una unidad inmutable de evaluacion leida del dataset."""

    id: str
    description: str
    source_filename: str
    source_code: str
    test_filename: str
    tags: tuple[str, ...]

    def __post_init__(self) -> None:
        """Garantiza que los nombres temporales sean archivos Python simples."""
        for field_name, filename in (
            ("source_filename", self.source_filename),
            ("test_filename", self.test_filename),
        ):
            if (
                not isinstance(filename, str)
                or not filename.endswith(".py")
                or any(separator in filename for separator in ("/", "\\", ":", "\0"))
            ):
                raise ValueError(
                    f"{field_name} debe ser un nombre de archivo .py sin directorios."
                )

        if self.source_filename.casefold() == self.test_filename.casefold():
            raise ValueError("source_filename y test_filename deben ser distintos.")


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Parametros que pueden afectar a una generacion del modelo."""

    model: str
    temperature: float = 0.0
    timeout_seconds: float = 180.0
    max_tokens: int = 256


@dataclass(frozen=True, slots=True)
class GeneratedResponse:
    """Salida normalizada de cualquier proveedor de LLM."""

    text: str
    latency_ms: float
