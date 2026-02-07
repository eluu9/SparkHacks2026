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
            content = self._call_gemini(system_prompt, user_prompt)
        else:
            content = self._call_local(system_prompt, user_prompt, schema)

        parsed = json.loads(content)
        return parsed


    def _call_gemini(self, system_prompt, user_prompt):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=config.get("GeminiModelName"),
            contents=f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}",
            config={"response_mime_type": "application/json"},
        )

        text = getattr(response, "text", "") or ""
        if not text:
            try:
                parts = response.candidates[0].content.parts
                text = "".join(getattr(p, "text", "") for p in parts)
            except Exception:
                text = ""

        if not text:
            raise ValueError("Gemini returned an empty response")

        return text

    def _call_local(self, system_prompt, user_prompt, schema):
        body = {
            "model": config.get("LocalModelName"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": schema if schema is not None else "json",
        }

        resp = requests.post(config.get("LocalModelUrl"), json=body, timeout=240)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")


def validate_response(response, schema):
    if schema is None:
        return response
    jsonschema.validate(instance=response, schema=schema)
    return response


def convert_schema_to_dict(schema_path):
    return json.loads(Path(schema_path).read_text(encoding="utf-8"))