"""
backend/routes/face.py

POST /analyze-face

Accepts a multipart image file upload and returns a face-based stroke risk score.

Pipeline:
    1.  Read uploaded image bytes
    2.  Load + resize + normalize (preprocessing.py)
    3.  Detect face region and compute geometric symmetry metrics (feature_extraction.py)
    4.  Run the CNN model to get a raw visual risk score (face_model.py)
    5.  Fuse: face_risk_score = 0.5 * cnn_score + 0.5 * symmetry_deviation
    6.  Return structured JSON response
"""

import logging
import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..utils.preprocessing import preprocess_image_for_cnn
from ..utils.feature_extraction import compute_facial_symmetry, extract_face_region
from ..models.face_model.face_model import predict as face_predict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-face", summary="Analyze facial stroke risk from an image")
async def analyze_face(
    image: UploadFile = File(..., description="Face image (JPEG/PNG/BMP)"),
    age: float = 0,
    bp: str = "",
    glucose: float = 0
):
    """
    Analyze a facial image for stroke-related asymmetry and risk.
    """
    # ── 1. Validate content type ──────────────────────────────────────────────
    allowed_types = {"image/jpeg", "image/png", "image/bmp", "image/webp", "image/jpg"}
    ct = (image.content_type or "").lower()
    if ct not in allowed_types and not ct.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type: {ct}. Please upload a JPEG or PNG image.",
        )

    # ── 2. Read bytes ─────────────────────────────────────────────────────────
    try:
        file_bytes = await image.read()
        if len(file_bytes) < 100:
            raise HTTPException(status_code=400, detail="Image file appears to be empty or corrupted.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {exc}")

    # ── 3. Preprocess for CNN ─────────────────────────────────────────────────
    try:
        img_array = preprocess_image_for_cnn(file_bytes)   # (1, 224, 224, 3)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Image preprocessing failed: {exc}")

    # ── 4. Load raw image for symmetry analysis ──────────────────────────────
    try:
        import cv2, numpy as np
        nparr  = np.frombuffer(file_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as exc:
        logger.warning("Symmetry analysis unavailable: %s", exc)
        img_bgr = None

    # ── 5. CNN prediction (Model Confidence) ──────────────────────────────────
    try:
        cnn_score = face_predict(img_array)
    except Exception as exc:
        logger.error("Face CNN prediction failed: %s", exc)
        cnn_score = 0.5

    # ── 6. Symmetry & Clinical Analysis ────────────────────────────────────────
    symmetry_result = {"face_detected": False, "symmetry_deviation": 0.5}
    landmarks = []
    
    if img_bgr is not None:
        try:
            symmetry_result = compute_facial_symmetry(img_bgr)
            from ..dataset_module.preprocessing import extract_clinical_landmarks
            lm_array = extract_clinical_landmarks(img_bgr)
            if lm_array.any():
                landmarks = lm_array.reshape(-1, 3).tolist()
        except Exception as exc:
            logger.warning("Symmetry/Landmark computation error: %s", exc)

    symmetry_deviation = symmetry_result.get("symmetry_deviation", 0.5)
    face_detected      = symmetry_result.get("face_detected", False)

    # ── 7. Clinical Risk Factor (New) ─────────────────────────────────────────
    from ..utils.xai_engine import calculate_clinical_risk
    clinical_data = calculate_clinical_risk(age, bp, glucose)
    clinical_risk = clinical_data["clinical_score"]

    # ── 8. Fuse AI + Clinical Score ───────────────────────────────────────────
    # Logic: 60% Face AI (CNN + Symmetry) + 40% Clinical Metadata
    ai_face_score = (0.5 * cnn_score + 0.5 * symmetry_deviation) if face_detected else cnn_score
    
    # User's suggested upgrade: Integrate BP and Glucose
    face_risk_score = (0.6 * ai_face_score) + (0.4 * clinical_risk)
    face_risk_score = round(float(np.clip(face_risk_score, 0.0, 1.0)), 4)

    # ── 9. XAI Reasoning ────────────────────────────────────────────────────
    from ..utils.xai_engine import generate_face_explanation
    xai_data = generate_face_explanation(symmetry_result, clinical_data)

    # ── 10. Risk Labeling ───────────────────────────────────────────────────
    if face_risk_score < 0.30:
        risk_label = "Low Risk"
    elif face_risk_score < 0.60:
        risk_label = "Medium Risk"
    else:
        risk_label = "High Risk"

    # ── 11. Build response ───────────────────────────────────────────────────
    response = {
        "face_risk_score":   face_risk_score,
        "cnn_score":         round(cnn_score, 4),
        "symmetry_deviation": round(symmetry_deviation, 4),
        "clinical_risk":     round(clinical_risk, 4),
        "symmetry_details": {
            "face_detected":        face_detected,
            "landmarks":            landmarks,
        },
        "explanation":     xai_data,
        "face_detected":   face_detected,
        "risk_label":      risk_label,
        "recommendation":  xai_data["recommendation"],
        "model_version":   "v3.0-clinical",
    }

    # ── 11. Save to History ───────────────────────────────────────────────────
    from ..utils.history import save_analysis
    save_analysis(response)

    return JSONResponse(content=response)

