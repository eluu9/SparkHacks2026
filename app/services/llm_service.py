import json
import jsonschema
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
                content = self._call_groq(system_prompt, user_prompt, schema)
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

    def _call_groq(self, system_prompt, user_prompt, schema=None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        client = Groq(api_key=api_key)
        
        model_id = config.get("GroqModelName", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_prompt)}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content


def validate_response(response, schema):
    if schema is None:
        return response
    jsonschema.validate(instance=response, schema=schema)
    return response


def convert_schema_to_dict(schema_path):
    return json.loads(Path(schema_path).read_text(encoding="utf-8"))