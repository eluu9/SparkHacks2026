import json
import jsonschema
import requests
import os
from groq import Groq
from pathlib import Path


config = json.loads(Path("app/config.json").read_text(encoding="utf-8"))


class LocalLLMProvider:
    def generate_response(self, system_prompt, user_prompt, schema, max_retries=2):
        if isinstance(system_prompt, dict):
            system_prompt = json.dumps(system_prompt)
        if isinstance(user_prompt, dict):
            user_prompt = json.dumps(user_prompt)
            
        for attempt in range(max_retries + 1):
            try:
                if config.get("UsingGroq"):
                    content = self._call_groq(system_prompt, user_prompt, schema)
                else:
                    content = self._call_local(system_prompt, user_prompt, schema)

                parsed = json.loads(content)
                
                if schema is not None:
                    jsonschema.validate(instance=parsed, schema=schema)
                
                return parsed
                
            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                if attempt < max_retries:
                    repair_hint = f"\n\nPREVIOUS ATTEMPT FAILED: {str(e)}\nPlease fix the JSON structure and ensure it matches the schema exactly."
                    system_prompt = system_prompt + repair_hint
                    continue
                else:
                    raise

    def _call_groq(self, system_prompt, user_prompt, schema):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        client = Groq(api_key=api_key)
        
        messages = [
            {"role": "system", "content": str(system_prompt)},
            {"role": "user", "content": str(user_prompt)}
        ]
        
        response = client.chat.completions.create(
            model=config.get("GroqModelName"),
            messages=messages,
            temperature=0.3, # adjusted for a little more "creativity" -> answers were sometimes the exact same
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content

    def _call_local(self, system_prompt, user_prompt, schema):
        body = {
            "model": config.get("LocalModelName"),
            "messages": [
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_prompt)},
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