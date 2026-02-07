import json
import jsonschema
import requests
import os
from google import genai

from pathlib import Path

config = json.loads(Path("app/config.json").read_text(encoding="utf-8"))

class LocalLLMProvider:
    def generate_response(self, system_prompt, user_prompt, schema):
        if config.get("UsingGemini"): 
            client = genai.Client(os.getenv("GEMINI_API_KEY"))
            if client is None:
                raise ValueError("GEMINI_API_KEY environment variable not set")

            response = client.models.generate_content(
                model=config.get("GeminiModelName"),
                contents=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format=schema if schema is not None else "json"
            )
        else:
            prompt = {
                "model": config.get("LocalModelName"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            }

            # json format fallback if no schema is provided -> suggested by copilot
            if schema is not None:
                prompt["format"] = schema
            else:
                prompt["format"] = "json"

            response = requests.post(f"{config.get('LocalModelUrl')}", json=prompt, timeout=240)
            response.raise_for_status()
        
        data = response.json()
        content = data.get("message", {}).get("content", "")

        return json.loads(content)

def validate_response(response, schema):
    if schema is None:
        return response

    # Checks if the json returned by the LLM matches the provided schema 
    jsonschema.validate(instance=response, schema=schema)
    return response

def convert_schema_to_dict(schema_str):
    try:
        return json.loads(Path(schema_str).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON schema: {e}")