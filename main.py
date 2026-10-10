from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import random

app = FastAPI(title="MgHub API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

async def call_gemini(message: str) -> str:
    if not GEMINI_API_KEY:
        return local_ai_response(message)
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = "Ti si MgHub AI asistent za auto-eko sustav BiH. Odgovori kratko na bosanskom: " + message
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini error: " + str(e))
        return local_ai_response(message)

def local_ai_response(msg: str) -> str:
    m = msg.lower()
    if "trust" in m:
        return "Trust Score raste +3 po recenziji, +15 bodova."
    if "vin" in m:
        return "VIN dekoder je u tabu Alati."
    if "vulkanizer" in m or "guma" in m:
        return "Usluge - filter Vulkanizeri."
    if "slep" in m:
        return "Usluge - filter Slep."
    if "bank" in m:
        return "Banke su u tabu Fintech."
    return "Pitaj me o: partnerima, vozilima, alatima, Trust Scoreu."

class ReviewIn(BaseModel):
    partner_id: int
    stars: int
    text: Optional[str] = ""

class OglasIn(BaseModel):
    title: str
    price: float
    cat: str
    city: str
    year: Optional[int] = None
    km: Optional[int] = None

class OrderIn(BaseModel):
    items: List[dict]
    payment_method: str = "card"

class SOSIn(BaseModel):
    sos_type: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class AIIn(BaseModel):
    message: str
    context: Optional[dict] = None

DB = {"reviews": [], "oglasi": [], "orders": [], "sos": []}

@app.get("/")
def root():
    return {"status": "ok", "app": "MgHub API", "version": "2.1.0"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/ai/chat")
async def ai_chat(data: AIIn):
    reply = await call_gemini(data.message)
    return {"reply": reply}

@app.get("/api/v1/reviews")
def get_reviews():
    return DB["reviews"]

@app.post("/api/v1/reviews")
def add_review(data: ReviewIn):
    r = {"id": len(DB["reviews"]) + 1, "partner_id": data.partner_id, "stars": data.stars, "text": data.text, "created_at": datetime.utcnow().isoformat()}
    DB["reviews"].append(r)
    return r

@app.get("/api/v1/oglasi")
def get_oglasi():
    return DB["oglasi"]

@app.post("/api/v1/oglasi")
def add_oglas(data: OglasIn):
    o = {"id": len(DB["oglasi"]) + 1, "title": data.title, "price": data.price, "cat": data.cat, "city": data.city, "created_at": datetime.utcnow().isoformat()}
    DB["oglasi"].append(o)
    return o

@app.post("/api/v1/orders")
def create_order(data: OrderIn):
    total = sum(item.get("price", 0) for item in data.items)
    o = {"id": len(DB["orders"]) + 1, "total": total, "status": "confirmed", "created_at": datetime.utcnow().isoformat()}
    DB["orders"].append(o)
    return o

@app.post("/api/v1/sos")
def send_sos(data: SOSIn):
    tracking = "#MG-" + str(random.randint(100000, 999999))
    s = {"id": len(DB["sos"]) + 1, "tracking_number": tracking, "sos_type": data.sos_type, "status": "dispatched", "created_at": datetime.utcnow().isoformat()}
    DB["sos"].append(s)
    return s

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
