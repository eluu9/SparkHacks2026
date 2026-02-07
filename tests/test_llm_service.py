import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_service import LocalLLMProvider, validate_response


def test_local_provider():
    provider = LocalLLMProvider()
    
    system_prompt = """You are an assistant that outputs JSON only. Return a single JSON object.
Decide whether the user request needs clarification. If yes, return need_clarification: true with 1-3 questions.
If no, return need_clarification: false with a task_interpretation."""
    
    user_prompt = "User prompt: I want to look at the moon"
    
    schema = {
        "type": "object",
        "required": ["need_clarification"],
        "properties": {
            "need_clarification": {"type": "boolean"},
            "questions": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    
    print("Calling LocalLLMProvider...")
    result = provider.generate_response(system_prompt, user_prompt, schema)
    print(f"Raw result: {result}")
    
    validated = validate_response(result, schema)
    print(f"Validated result: {validated}")
    
    assert "need_clarification" in validated
    print("✓ Test passed!")


if __name__ == "__main__":
    test_local_provider()
