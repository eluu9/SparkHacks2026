"""LLM integration layer (Groq) with JSON schema validation and retry logic."""

import json
import os
from pathlib import Path

import jsonschema
from groq import Groq

config = json.loads(Path("app/config.json").read_text(encoding="utf-8"))


class LocalLLMProvider:
    """Calls Groq and validates the JSON response against a schema."""

    def generate_response(self, system_prompt, user_prompt, schema, max_retries=2):
        """Send prompts to the LLM with automatic retry on malformed JSON."""
        if isinstance(system_prompt, dict):
            system_prompt = json.dumps(system_prompt)
        if isinstance(user_prompt, dict):
            user_prompt = json.dumps(user_prompt)

        for attempt in range(max_retries + 1):
            try:
                content = self._call_groq(system_prompt, user_prompt)
                parsed = json.loads(content)

                if schema is not None:
                    jsonschema.validate(instance=parsed, schema=schema)

                return parsed

            except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
                if attempt < max_retries:
                    repair_hint = (
                        f"\n\nPREVIOUS ATTEMPT FAILED: {exc}\n"
                        "Please fix the JSON structure and ensure it "
                        "matches the schema exactly."
                    )
                    system_prompt = system_prompt + repair_hint
                    continue
                raise

    def _call_groq(self, system_prompt, user_prompt):
        """Make a single completion request to the Groq API."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        client = Groq(api_key=api_key)
        model_id = config.get("GroqModelName", "llama-3.3-70b-versatile")

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_prompt)},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content


def validate_response(response, schema):
    """Validate a parsed dict against a JSON schema (no-op if schema is None)."""
    if schema is None:
        return response
    jsonschema.validate(instance=response, schema=schema)
    return response


def convert_schema_to_dict(schema_path):
    """Read a .json schema file and return it as a dict."""
    return json.loads(Path(schema_path).read_text(encoding="utf-8"))