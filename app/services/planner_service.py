"""Clarification gate — decides if the LLM needs to ask follow-up questions."""

from pathlib import Path

from app.services.llm_service import (
    LocalLLMProvider,
    convert_schema_to_dict,
    validate_response,
)


def gate_clarification(user_prompt, conversation_history=None, user_preferences=None):
    """Run the clarification gate and return validated LLM output."""
    clarify_gate_str = Path(
        "app/services/prompts/clarify_gate.md"
    ).read_text(encoding="utf-8")
    llm = LocalLLMProvider()

    if conversation_history and isinstance(conversation_history, list):
        history_str = "\n".join(
            f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
            for item in conversation_history
        )
    else:
        history_str = str(conversation_history or "")

    formatted_prompt = clarify_gate_str.format(
        user_prompt=user_prompt,
        conversation_history=history_str,
        user_preferences=user_preferences or "",
    )

    schema = convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=user_prompt,
        schema=schema,
    )

    return validate_response(response, schema)
