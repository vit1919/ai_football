import json
import logging
from google import genai
from google.genai import errors as genai_errors
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.google_api_key)


async def call_llm(prompt: str, model_name: str | None = None) -> dict:
    client = _get_client()
    model = model_name or settings.llm_default_model
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
        )
    except (genai_errors.ClientError, genai_errors.ServerError) as e:
        logger.error("Gemini API error: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected LLM error: %s", e)
        raise

    text = (response.text or "").strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    logger.debug("LLM raw response: %s", repr(text)[:200])

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON: %s, text=%s", e, text[:200])
        raise
