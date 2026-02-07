import json
from app.services.llm_service import LocalLLMProvider, validate_response, convert_schema_to_dict
from pathlib import Path


def gate_clarification(user_prompt, conversation_history=None, user_preferences=None):
    clarify_gate_str = Path("app/services/prompts/clarify_gate.md").read_text(encoding="utf-8")
    llm = LocalLLMProvider()
    
    if conversation_history and isinstance(conversation_history, list):
        history_str = "\n".join([
            f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}" 
            for item in conversation_history
        ])
    else:
        history_str = str(conversation_history or "")
    
    formatted_prompt = clarify_gate_str.format(
        user_prompt=user_prompt,
        conversation_history=history_str,
        user_preferences=user_preferences or ""
    )

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=user_prompt,
        schema=convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    )

    validated_response = validate_response(response, convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json"))
    return validated_response

