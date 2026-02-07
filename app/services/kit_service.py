"""Kit generation — turns a task interpretation into a structured product kit."""

import json
from pathlib import Path

from app.services.llm_service import (
    LocalLLMProvider,
    convert_schema_to_dict,
    validate_response,
)


def generate_kit(task_interpretation, clarifications=None, user_preferences=None):
    """Send the task and context to the LLM and return a validated kit JSON."""
    kit_prompt_str = Path(
        "app/services/prompts/kit_builder.md"
    ).read_text(encoding="utf-8")
    llm = LocalLLMProvider()

    if isinstance(task_interpretation, dict):
        task_str = json.dumps(task_interpretation)
    else:
        task_str = str(task_interpretation)

    formatted_prompt = kit_prompt_str.format(
        task_interpretation=task_str,
        clarifications=clarifications or "",
        user_preferences=user_preferences or "",
    )

    schema = convert_schema_to_dict("app/schemas/kit.schema.json")

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=task_str,
        schema=schema,
    )

    return validate_response(response, schema)