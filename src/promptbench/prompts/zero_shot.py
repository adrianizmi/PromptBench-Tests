"""Estrategia zero-shot para generar tests Python."""

from pathlib import Path

from promptbench.domain import EvaluationCase
from promptbench.prompts.base import PromptStrategy


class ZeroShotPromptStrategy(PromptStrategy):
    """Estrategia que construye prompts sin ejemplos previos."""

    def build(self, case: EvaluationCase) -> str:
        """Devuelve el prompt zero-shot para un caso de evaluacion."""
        return build_zero_shot_prompt(case)


def build_zero_shot_prompt(case: EvaluationCase) -> str:
    """Construye un prompt sin ejemplos previos."""
    module_name = Path(case.source_filename).stem

    return f"""
Eres un desarrollador experto en tests automatizados con pytest en Python.

Tu objetivo es escribir tests del siguiente codigo.

Descripcion:
{case.description}

Archivo de codigo:
{case.source_filename}

Modulo Python que debes importar:
{module_name}

Reglas de importacion:
- Importa siempre las funciones necesarias desde el modulo {module_name}.
- Usa imports con este formato: from {module_name} import <funciones_necesarias>
- No asumas que las funciones existen en el entorno global.
- Incluye los imports explicitos al inicio del archivo de test.

Requisitos de los tests:
- Escribe al menos una funcion cuyo nombre empiece por test_.
- Cada funcion de test debe contener al menos una asercion.
- Escribe entre una y tres funciones de test, con un maximo de cinco aserciones en total.
- Comprueba valores normales y, si procede, uno o dos casos limite representativos.
- Usa entradas pequenas y evita repetir comprobaciones equivalentes.
- No te limites a escribir los imports: la respuesta debe incluir el cuerpo de los tests.
- Usa solo funciones y comportamientos que aparezcan en el codigo o la descripcion.
- Asegurate de cerrar parentesis y corchetes y de terminar el archivo con codigo Python completo.

Codigo:
{case.source_code}

Archivo de test a generar:
{case.test_filename}

Formato de salida obligatorio:
- Devuelve exclusivamente codigo Python valido.
- La primera linea de tu respuesta debe ser una sentencia Python, un import o una definicion.
- La respuesta debe incluir al menos una funcion test_ con aserciones ejecutables.
- No incluyas Markdown.
- No incluyas bloques ```python.
- No incluyas bloques ```.
- No incluyas explicaciones antes ni despues del codigo.
""".strip()
