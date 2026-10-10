from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_gemini_client = None

def get_gemini_client():
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client

async def call_gemini(message: str) -> str:
    client = get_gemini_client()
    if not client:
        return local_ai_response(message)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Ti si MgHub AI asistent za auto-eko sustav BiH. Odgovori kratko na bosanskom: " + message
        )
        return response.text
    except Exception as e:
        print("Gemini error: " + str(e))
        return local_ai_response(message)
