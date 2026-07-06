import os
import time
from google import genai
from google.genai import types

_client = None

def getClient():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client

def generateGroundedReply(systemInstruction: str, userPrompt: str, maxOutputTokens: int = 400) -> str:
    """
    All modules funnel through this one function.
    systemInstruction: sets role + hard constraints (language, no invented facts, tone).
    userPrompt: the grounded facts + actual question, assembled by the calling service.py.
    Retries automatically on 429 TooManyRequests with exponential backoff.
    """
    client = getClient()
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    MAX_RETRIES = 4
    BACKOFF_SECONDS = [2, 5, 10, 20]  # wait times between retries

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model,
                contents=userPrompt,
                config=types.GenerateContentConfig(
                    system_instruction=systemInstruction,
                    max_output_tokens=maxOutputTokens,
                    temperature=0.3,
                ),
            )
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            # Retry only on rate limit errors
            if "429" in error_str or "too many requests" in error_str or "resource_exhausted" in error_str:
                wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                time.sleep(wait)
                continue
            # For all other errors, fail immediately
            raise e

    # All retries exhausted
    # raise last_error
