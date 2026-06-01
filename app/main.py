# FastAPI Server Entrypoint for ApexBank AI Co-Pilot
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

from .banking_data import CUSTOMER_PROFILES, TRANSACTIONS, DISPUTES, BANK_RATES
from .agents import coordinate_agents, GEMINI_AVAILABLE
import google.generativeai as genai

app = FastAPI(title="ApexBank AI Co-Pilot Dashboard")

# Get paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Request Models
class ChatRequest(BaseModel):
    customer_id: str
    message: str

class APIKeyRequest(BaseModel):
    api_key: str

class LockCardRequest(BaseModel):
    customer_id: str
    card_id: str

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    # Retrieve customer data to pre-populate list on client
    customers_list = [
        {"id": cid, "name": profile["name"]} 
        for cid, profile in CUSTOMER_PROFILES.items()
    ]
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "customers": customers_list,
            "gemini_active": bool(os.getenv("GEMINI_API_KEY") or GEMINI_AVAILABLE)
        }
    )

@app.get("/api/customer/{customer_id}")
async def get_customer_data(customer_id: str):
    profile = CUSTOMER_PROFILES.get(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    txns = TRANSACTIONS.get(customer_id, [])
    disputes = [d for d in DISPUTES if d["customer_id"] == customer_id]
    
    return {
        "profile": profile,
        "transactions": txns,
        "disputes": disputes
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.customer_id or not req.message:
        raise HTTPException(status_code=400, detail="Invalid request parameters")
    
    try:
        result = coordinate_agents(req.customer_id, req.message)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent coordination failed: {str(e)}")

@app.post("/api/lock_card")
async def lock_card_endpoint(req: LockCardRequest):
    profile = CUSTOMER_PROFILES.get(req.customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    card_found = False
    for card in profile.get("credit_cards", []):
        if card["card_id"] == req.card_id:
            card["status"] = "Locked"
            card_found = True
            break
            
    if not card_found:
        raise HTTPException(status_code=404, detail="Card not found")
        
    return {"status": "success", "message": f"Credit Card {req.card_id} has been securely locked."}

@app.post("/api/api_key")
async def configure_api_key(req: APIKeyRequest):
    if not req.api_key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty")
    
    # Configure Google Generative AI with the key dynamically
    try:
        genai.configure(api_key=req.api_key)
        os.environ["GEMINI_API_KEY"] = req.api_key
        # Check simple connection if possible, or just accept
        global GEMINI_AVAILABLE
        GEMINI_AVAILABLE = True
        return {"status": "success", "message": "Gemini API Key configured successfully. Live mode is now active!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to configure Gemini SDK: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
