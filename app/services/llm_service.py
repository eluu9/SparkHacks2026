import json
import jsonschema
import requests
import os

from pathlib import Path


config = json.loads(Path("app/config.json").read_text(encoding="utf-8"))

class LocalLLMProvider:
    def generate_response(self, system_prompt, user_prompt, schema):
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

# class GeminiProvider:
#     def __init__(self, api_key=None, model=None, base_url=None):
#         self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
#         self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
#         self.base_url = base_url or os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models")

#     def generate_response(self, system_prompt, user_prompt, schema):
#         url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
#         payload = {
#             "contents": [
#                 {
#                     "role": "user",
#                     "parts": [
#                         {"text": system_prompt},
#                         {"text": user_prompt},
#                     ],
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.2,
#                 "responseMimeType": "application/json",
#             },
#         }
#         if schema is not None:
#             payload["generationConfig"]["responseSchema"] = schema

#         response = requests.post(url, json=payload, timeout=30)
#         response.raise_for_status()
#         data = response.json()
#         text = (
#             data.get("candidates", [{}])[0]
#             .get("content", {})
#             .get("parts", [{}])[0]
#             .get("text", "")
#         )
#         try:
#             return json.loads(text)
#         except json.JSONDecodeError:
#             return {"text": text}

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