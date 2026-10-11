"""Zero-shot strategy for generating Python tests."""

from pathlib import Path

from promptbench.domain import EvaluationCase
from promptbench.prompts.base import PromptStrategy


class ZeroShotPromptStrategy(PromptStrategy):
    """A strategy that builds prompts without prior examples."""

    def build(self, case: EvaluationCase) -> str:
        """Return the zero-shot prompt for an evaluation case."""
        return build_zero_shot_prompt(case)


def build_zero_shot_prompt(case: EvaluationCase) -> str:
    """Build a prompt without prior examples."""
    module_name = Path(case.source_filename).stem

    return f"""
You are an expert Python developer specializing in automated pytest tests.

Your goal is to write tests for the following code.

Description:
{case.description}

Source file:
{case.source_filename}

Python module to import:
{module_name}

Import rules:
- Always import the required functions from the {module_name} module.
- Use imports in this format: from {module_name} import <required_functions>
- Do not assume functions exist in the global environment.
- Include explicit imports at the beginning of the test file.

Test requirements:
- Write at least one function whose name starts with test_.
- Each test function must contain at least one assertion.
- Write between one and three test functions, with at most five assertions in total.
- Check normal values and, where applicable, one or two representative edge cases.
- Use small inputs and avoid repeating equivalent checks.
- Do not only write imports: the response must include the test bodies.
- Use only functions and behavior that appear in the code or description.
- Make sure parentheses and brackets are closed, and finish with complete Python code.

Code:
{case.source_code}

Test file to generate:
{case.test_filename}

Required output format:
- Return valid Python code only.
- The first line of your response must be a Python statement, an import, or a definition.
- The response must include at least one test_ function with executable assertions.
- Do not include Markdown.
- Do not include ```python blocks.
- Do not include ``` blocks.
- Do not include explanations before or after the code.
""".strip()
