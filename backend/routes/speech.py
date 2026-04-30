"""
backend/routes/speech.py

POST /analyze-speech

Accepts a multipart audio file upload and returns a speech-based stroke risk score.

Pipeline:
    1.  Read uploaded audio bytes
    2.  Load audio with librosa + pad/trim to 3 seconds (preprocessing.py)
    3.  Extract 122-dim MFCC feature vector (feature_extraction.py)
    4.  Run CNN/LSTM model → emotion probs → stroke-risk score (speech_model.py)
    5.  Return structured JSON response
"""

import logging
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..utils.preprocessing import load_audio, pad_or_trim_audio
from ..utils.feature_extraction import extract_mfcc_features
from ..models.speech_model.speech_model import predict as speech_predict

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed audio MIME types (WAV, MP3, OGG, FLAC, WebM audio)
ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/ogg", "audio/flac",
    "audio/webm", "application/octet-stream",   # some browsers send generic type
}


@router.post("/analyze-speech", summary="Analyze speech for stroke-related abnormalities")
async def analyze_speech(
    audio: UploadFile = File(..., description="Audio file (WAV/MP3/OGG/FLAC)"),
    age: float = 0,
    bp: str = "",
    glucose: float = 0
):
    """
    Analyze an audio file for stroke-related speech abnormalities (dysarthria / slurring).
    """
    # ── 1. Validate content type ──────────────────────────────────────────────
    ct = (audio.content_type or "").lower()
    if ct not in ALLOWED_AUDIO_TYPES and not ct.startswith("audio/"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type: '{ct}'",
        )

    # ── 2. Read bytes ─────────────────────────────────────────────────────────
    try:
        file_bytes = await audio.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}")

    # ── 3. Load + preprocess audio ────────────────────────────────────────────
    try:
        y, sr = load_audio(file_bytes)
        y     = pad_or_trim_audio(y, sr * 3)
        audio_duration_s = round(len(y) / sr, 2)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Audio preprocessing failed: {exc}")

    # ── 4. Extract MFCC features ──────────────────────────────────────────────
    try:
        mfcc_features = extract_mfcc_features(y, sr)
        feature_dim   = int(mfcc_features.shape[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Feature extraction error: {exc}")

    # ── 5. Model prediction ───────────────────────────────────────────────────
    try:
        result = speech_predict(mfcc_features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Speech model error: {exc}")

    ai_speech_score = result["speech_risk_score"]

    # ── 6. Clinical Risk Factor ──────────────────────────────────────────────
    from ..utils.xai_engine import calculate_clinical_risk
    clinical_data = calculate_clinical_risk(age, bp, glucose)
    clinical_risk = clinical_data["clinical_score"]

    # ── 7. Fuse AI + Clinical Score ──────────────────────────────────────────
    speech_risk_score = (0.7 * ai_speech_score) + (0.3 * clinical_risk)
    speech_risk_score = round(float(np.clip(speech_risk_score, 0.0, 1.0)), 4)

    # ── 8. XAI Reasoning ─────────────────────────────────────────────────────
    from ..utils.xai_engine import generate_speech_explanation
    xai_data = generate_speech_explanation(speech_risk_score, mfcc_features.tolist(), clinical_data)

    # ── 9. Risk label ─────────────────────────────────────────────────────────
    if speech_risk_score < 0.30:
        risk_label = "Low Risk"
    elif speech_risk_score < 0.60:
        risk_label = "Medium Risk"
    else:
        risk_label = "High Risk"

    # ── 10. Build response ─────────────────────────────────────────────────────
    response = {
        "speech_risk_score":    speech_risk_score,
        "clinical_risk":        round(clinical_risk, 4),
        "detected_emotion":     result.get("detected_emotion", "unknown"),
        "explanation":          xai_data,
        "risk_label":    risk_label,
        "recommendation": xai_data["recommendation"],
        "model_version": "v3.0-clinical",
    }
    return JSONResponse(content=response)

