"""Data models exchanged between experiment layers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    """An immutable evaluation unit read from the dataset."""

    id: str
    description: str
    source_filename: str
    source_code: str
    test_filename: str
    tags: tuple[str, ...]

    def __post_init__(self) -> None:
        """Ensure temporary filenames are simple Python files."""
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
                    f"{field_name} must be a .py filename without directories."
                )

        if self.source_filename.casefold() == self.test_filename.casefold():
            raise ValueError("source_filename and test_filename must be different.")


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Parameters that can affect model generation."""

    model: str
    temperature: float = 0.0
    timeout_seconds: float = 180.0
    max_tokens: int = 256


@dataclass(frozen=True, slots=True)
class GeneratedResponse:
    """Normalized output from any LLM provider."""

    text: str
    latency_ms: float
