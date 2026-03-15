from groq import Groq
from groq import RateLimitError
from key_rotator import KeyRotator

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a friendly, helpful AI voice assistant in a Discord voice channel. "
    "Keep your answers concise and conversational — typically 1-3 sentences. "
    "Avoid markdown formatting, bullet points, or headers since your responses will be spoken aloud."
)


def get_ai_response(text: str, rotator: KeyRotator, max_retries: int = None) -> str:
    if max_retries is None:
        max_retries = rotator.total()

    for attempt in range(max_retries):
        try:
            client = Groq(api_key=rotator.current())
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                max_tokens=256,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            print(f"[AI] Rate limit hit on key {rotator.current_index() + 1}, rotating...")
            rotator.rotate()
        except Exception as e:
            print(f"[AI] Error: {e}")
            raise

    return "Sorry, I am currently rate limited. Please try again in a moment."
