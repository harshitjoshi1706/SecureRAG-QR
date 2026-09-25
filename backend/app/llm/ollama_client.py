import json
import ollama

from app.llm.structured_output import CompactAnswer


MODEL_NAME = "qwen3:4b"


def generate_structured_answer(prompt: str) -> CompactAnswer:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    raw_content = response["message"]["content"]

    data = json.loads(raw_content)

    validated = CompactAnswer(**data)

    return validated