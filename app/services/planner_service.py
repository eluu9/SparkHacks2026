from app.services.llm_service import LocalLLMProvider, validate_response, convert_schema_to_dict
from pathlib import Path

def gate_clarification(user_prompt, conversation_history=None, user_preferences=None):
    clarify_gate_str = Path("app/services/prompts/clarify_gate.md").read_text(encoding="utf-8")
    llm = LocalLLMProvider()
    
    formatted_prompt = clarify_gate_str.format(
        user_prompt=user_prompt,
        conversation_history=conversation_history or "",
        user_preferences=user_preferences or ""
    )

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=user_prompt,
        schema=convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    )

    validated_response = validate_response(response, convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json"))
    return validated_response

