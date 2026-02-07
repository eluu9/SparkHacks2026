import json
from pathlib import Path
from app.services.llm_service import LocalLLMProvider, validate_response, convert_schema_to_dict

def generate_kit(task_interpretation, clarifications=None, user_preferences=None):
    kit_prompt_str = Path("app/services/prompts/kit_builder.md").read_text(encoding="utf-8")
    llm = LocalLLMProvider()
    
    task_str = json.dumps(task_interpretation) if isinstance(task_interpretation, dict) else str(task_interpretation)
    
    formatted_prompt = kit_prompt_str.format(
        task_interpretation=task_str,
        clarifications=clarifications or "",
        user_preferences=user_preferences or ""
    )

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=task_str,
        schema=convert_schema_to_dict("app/schemas/kit.schema.json")
    )

    validated_response = validate_response(response, convert_schema_to_dict("app/schemas/kit.schema.json"))
    return validated_response
