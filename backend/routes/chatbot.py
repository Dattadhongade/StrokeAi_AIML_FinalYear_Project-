"""
backend/routes/chatbot.py

Chatbot API for stroke risk explanation, medical FAQ, and emergency guidance.
Integrates with Google Gemini for "Unlimited" medical knowledge if an API key is provided.
Falls back to a robust rule-based system if offline or no key is found.
"""

import logging
import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, Body
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Gemini Integration ────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

try:
    if GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("✓ Gemini AI engine initialized for 'Unlimited' medical data.")
    else:
        logger.warning("! GEMINI_API_KEY not found. Using local rule-based system.")
except Exception as e:
    logger.error("Failed to initialize Gemini: %s", e)

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    emergency: bool = False

# ── Local Knowledge Base (Fallback) ──────────────────────────────────────────
KNOWLEDGE_BASE = {
    "stroke": (
        "A stroke occurs when the blood supply to part of your brain is interrupted or reduced, "
        "preventing brain tissue from getting oxygen and nutrients. Brain cells begin to die in minutes. "
        "There are three main types: Ischemic, Hemorrhagic, and TIA."
    ),
    "fast": (
        "FAST is the primary mnemonic for stroke detection: Face drooping, Arm weakness, Speech difficulty, and Time to call emergency services."
    ),
    "tablets": (
        "Medications for stroke management often include Antiplatelets (Aspirin), Anticoagulants, Statins, and Antihypertensives."
    ),
    "viruses": (
        "Infections like COVID-19 or meningitis can increase stroke risk by causing inflammation or blood clotting."
    ),
    "hospitals": (
        "Hospital diagnostics include CT Scans, MRIs, Carotid Ultrasounds, and Echocardiograms."
    ),
    "prevention": (
        "Stroke prevention focuses on managing blood pressure, cholesterol, diabetes, staying active, and stopping smoking."
    )
}

# ── Intent Detection Logic ────────────────────────────────────────────────────

def detect_intent(message: str) -> str:
    msg = message.lower().strip()
    
    if msg in ["hi", "hello", "hey", "yo"]: return "greeting"
    if any(w in msg for w in ["thank", "thanks", "great", "awesome"]): return "thanks"
    if any(w in msg for w in ["why", "explain", "reason", "how"]): return "explain_results"
    if any(w in msg for w in ["do", "help", "action", "emergency"]): return "guide_action"
    if any(w in msg for w in ["report", "score", "analysis"]): return "interpret_report"
    
    return "general_query"

# ── Response Generation ───────────────────────────────────────────────────────

async def get_gemini_response(prompt: str, context: Optional[Dict[str, Any]]) -> str:
    """Uses Google Gemini to provide 'Unlimited' medical knowledge."""
    if not model: return None
    
    system_prompt = (
        "You are 'StrokeAI Assistant', an expert medical AI specializing in stroke risk detection. "
        "You have access to 'unlimited' medical data. Answer the user's question with detailed, professional, "
        "and accurate medical information. If analysis results are provided in the context, interpret them. "
        "Always remind the user that this is for informational purposes and they should consult a doctor."
    )
    
    context_str = f"\nUser's Current Analysis: {context}" if context else ""
    full_prompt = f"{system_prompt}\n\nContext: {context_str}\nUser Question: {prompt}\nAnswer:"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        logger.error("Gemini Error: %s", e)
        return None

def get_fallback_response(intent: str, message: str, context: Optional[Dict[str, Any]]) -> ChatResponse:
    """Rule-based fallback if Gemini is unavailable."""
    res = ChatResponse(response="I'm here to help. You can ask about your results, what a stroke is, or symptoms to watch for.", intent=intent)
    
    if intent == "greeting":
        res.response = "Hello! I am your StrokeAI assistant. How can I help you today?"
    elif intent == "thanks":
        res.response = "You're welcome! Stay safe."
    elif intent == "explain_results":
        if context:
            f = context.get("face_analysis", {}).get("face_risk_score", 0)
            s = context.get("speech_analysis", {}).get("speech_risk_score", 0)
            res.response = f"Your risk is based on Face Asymmetry ({f*100:.1f}%) and Speech Abnormality ({s*100:.1f}%)."
        else:
            res.response = "Please complete an analysis first so I can explain your results."
    elif intent == "interpret_report":
        res.response = f"Your current risk level is {context.get('risk_label', 'Unknown')} with a score of {context.get('final_score', 0)}." if context else "No report found."
    else:
        # Check KB
        msg = message.lower()
        for key, val in KNOWLEDGE_BASE.items():
            if key in msg:
                res.response = val
                break
                
    return res

@router.post("/chat", response_model=ChatResponse, summary="Chat with StrokeAI (Gemini Powered)")
async def chat(payload: ChatRequest):
    """
    Handles user messages. Uses Gemini AI for broad medical knowledge, 
    falling back to local rules if needed.
    """
    intent = detect_intent(payload.message)
    
    # Check for Emergency first (Rule-based for safety)
    if payload.context and payload.context.get("final_score", 0) > 0.65:
        return ChatResponse(
            response="⚠️ HIGH STROKE RISK DETECTED. Call emergency services (911/112) immediately.",
            intent="emergency_alert",
            emergency=True
        )

    # Try Gemini for "Unlimited" data
    gemini_text = await get_gemini_response(payload.message, payload.context)
    if gemini_text:
        return ChatResponse(response=gemini_text, intent="gemini_ai")
    
    # Fallback to Local Rules
    return get_fallback_response(intent, payload.message, payload.context)
