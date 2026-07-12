import json
from google import genai
from app.core.config import settings


def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.google_api_key)


async def call_llm(prompt: str, model_name: str | None = None) -> dict:
    client = _get_client()
    model = model_name or settings.llm_default_model
    response = await client.aio.models.generate_content(
        model=model,
        contents=prompt,
    )
    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    print("RAW RESPONSE:")
    print(repr(text))
    return json.loads(text)
