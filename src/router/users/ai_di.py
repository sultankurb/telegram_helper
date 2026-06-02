from typing import Optional

from google import genai

from src.app_setup import settings

client = genai.Client(api_key=settings.GEMINI_API_KEYS)


async def make_response(question: str) -> Optional[str]:
    response  = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=question,
        config=genai.types.GenerateContentConfig(
            system_instruction="Отвечай на вопросы максимально точно"
                               " будто ты спец в этом деле",
            temperature=0.55,
        )
    )
    return response.text
