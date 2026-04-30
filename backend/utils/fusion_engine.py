"""
backend/utils/fusion_engine.py

Clinically-valid, mathematically consistent Multi-Modal Fusion Engine.
Designed for StrokeAI Research-Grade Diagnostics.
"""

from typing import Dict, List, Any

def calculate_clinical_score(age: float, bp_high: bool, sugar_high: bool) -> Dict[str, Any]:
    """
    Requirements:
    - High BP  -> +20 risk
    - High Sugar -> +20 risk
    - Age > 55 -> +15 risk
    Normalize to 0-100.
    """
    raw_score = 0
    reasons = []

    if bp_high:
        raw_score += 20
        reasons.append("Hypertension (High BP) detected - Primary vascular risk factor.")
    
    if sugar_high:
        raw_score += 20
        reasons.append("Hyperglycemia (High Sugar) detected - Metabolic risk factor.")
    
    if age > 55:
        raw_score += 15
        reasons.append(f"Age factor ({int(age)}) - Increased stroke vulnerability.")

    # Normalization: Assuming 55 is the clinical max for these markers
    # We'll normalize to 100 as per requirement
    normalized_score = (raw_score / 55) * 100 if raw_score > 0 else 0
    
    return {
        "score": round(normalized_score, 1),
        "reasons": reasons
    }

def fusion_engine(face_score: float, speech_score: float, clinical_score: float) -> Dict[str, Any]:
    """
    Mathematically Consistent Weighted Fusion.
    face_score, speech_score: 0-100
    clinical_score: 0-100
    
    Weights (Institutional Standard):
    - Face: 0.5 (Primary indicator)
    - Speech: 0.3
    - Clinical: 0.2
    """
    # 1. Weights
    w_face = 0.5
    w_speech = 0.3
    w_clinical = 0.2

    # 2. Final Score Calculation
    final_score = (w_face * face_score) + (w_speech * speech_score) + (w_clinical * clinical_score)
    final_score = round(final_score, 1)

    # 3. Dynamic Risk Classification
    # 0–20 → LOW, 21–50 → MEDIUM, 51–100 → HIGH
    if final_score <= 20:
        risk_level = "LOW"
    elif final_score <= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # 4. Explainable Output Generation
    explanations = []
    
    if face_score > 50:
        explanations.append("Significant facial asymmetry detected (Drooping side prioritized)")
    elif face_score > 20:
        explanations.append("Mild facial asymmetry detected")
    else:
        explanations.append("Facial symmetry is within normal parameters")

    if speech_score > 50:
        explanations.append("Speech abnormality (Dysarthria/Slurring) detected - increasing risk")
    elif speech_score > 20:
        explanations.append("Minor prosodic irregularities detected in speech")
    else:
        explanations.append("Speech patterns are clear and articulate - reducing risk")

    if clinical_score > 0:
        explanations.append("Clinical risk factors (Age/BP/Sugar) present and factored")

    return {
        "face_score": round(face_score, 1),
        "speech_score": round(speech_score, 1),
        "clinical_score": round(clinical_score, 1),
        "final_score": final_score,
        "risk_level": risk_level,
        "explanation": explanations,
        "formula": f"({w_face} * {face_score}) + ({w_speech} * {speech_score}) + ({w_clinical} * {clinical_score})"
    }
