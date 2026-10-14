import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime
from google import genai

app = FastAPI(title="MgHub API", version="1.0")

# CORS podešavanje da stranica s Neocities-a može komunicirati s API-jem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicijalizacija Gemini klijenta preko environment varijable
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

class AIIn(BaseModel):
    message: str
    context: Optional[dict] = None

DB = {
    "reviews": [],
    "oglasi": [],
    "orders": [],
    "sos": []
}

@app.get("/")
def root():
    return {"status": "ok", "app": "MgHub API"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/ai/chat")
async def ai_chat(data: AIIn):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API ključ nije podešen na serveru.")
    
    try:
        # Poziv prema Gemini modelu
        response = client.models.generate_content(
         model="gemini-2.0-flash", , 
            contents=data.message,
        )
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška s AI servisom: {str(e)}")

@app.get("/api/v1/reviews")
def get_reviews():
    return DB["reviews"]

@app.get("/api/v1/oglasi")
def get_oglasi():
    return DB["oglasi"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
                            
