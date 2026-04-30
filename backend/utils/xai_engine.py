"""
backend/utils/xai_engine.py

Explainable AI (XAI) engine for StrokeAI.
Provides human-readable reasoning and highlights areas of concern.
"""

from typing import Dict, Any, List

def calculate_clinical_risk(age: float = 0, bp: str = "", glucose: float = 0) -> Dict[str, Any]:
    """
    Calculates a clinical risk factor based on age, blood pressure, and glucose.
    """
    risk_score = 0.0
    reasons = []
    
    # Age factor (>55 is increased risk)
    if age > 55:
        age_risk = min((age - 55) / 40, 1.0) * 0.3
        risk_score += age_risk
        reasons.append(f"Advanced age ({int(age)}) increases baseline vascular risk.")
    
    # Blood Pressure factor (Hypertension > 140/90)
    if bp and "/" in bp:
        try:
            sys, dia = map(int, bp.split("/"))
            if sys > 140 or dia > 90:
                bp_risk = 0.4
                risk_score += bp_risk
                reasons.append(f"Hypertension detected ({bp}). High BP is the leading cause of stroke.")
        except:
            pass
            
    # Glucose factor (>140 is high risk/prediabetic)
    if glucose > 140:
        gl_risk = min((glucose - 140) / 200, 1.0) * 0.3
        risk_score += gl_risk
        reasons.append(f"Elevated glucose ({glucose} mg/dL) indicates metabolic risk.")
        
    return {
        "clinical_score": min(risk_score, 1.0),
        "reasons": reasons
    }

def generate_face_explanation(symmetry_data: Dict[str, Any], clinical_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generates an explanation for the face analysis result.
    """
    dev = symmetry_data.get("symmetry_deviation", 0)
    details = symmetry_data.get("details", "")
    
    reasons = []
    flagged_zones = []
    
    if dev > 0.65:
        reasons.append("CRITICAL: Significant facial drooping detected -> increasing risk.")
    elif dev > 0.35:
        reasons.append("MODERATE: Noticeable asymmetry in lower facial region detected.")
    else:
        reasons.append("STABLE: Face symmetry is within normal parameters -> reducing risk.")

    if "mouth" in details.lower():
        flagged_zones.append({"zone": "Lower Face / Mouth", "concern": "Potential drooping detected in oral commisures."})
    
    if "eye" in details.lower():
        flagged_zones.append({"zone": "Eye / Brow", "concern": "Asymmetry noted in palpebral fissure height."})
    
    if clinical_data and clinical_data.get("reasons"):
        reasons.extend(clinical_data["reasons"])
    
    if dev < 0.35:
        level = "Normal"
        rec = "No immediate clinical facial indicators for stroke detected."
    elif dev < 0.65:
        level = "Moderate Asymmetry"
        rec = "Mild facial drooping detected. Clinical correlation with arm/speech strength recommended."
    else:
        level = "Significant Asymmetry"
        rec = "SIGNIFICANT FACIAL DROOPING. This is a primary indicator for acute stroke. Act FAST."

    return {
        "analysis_level": level,
        "flagged_zones": flagged_zones,
        "reasons": reasons,
        "recommendation": rec,
        "confidence_score": 0.92
    }

def generate_speech_explanation(score: float, features: List[float], clinical_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generates an explanation for the speech analysis result.
    """
    reasons = []
    
    if score > 0.65:
        reasons.append("CRITICAL: Severe speech abnormality (dysarthria) detected -> increasing risk.")
    elif score > 0.35:
        reasons.append("MODERATE: Slurred speech or prosodic jitter detected.")
    else:
        reasons.append("STABLE: Speech patterns are articulate and clear -> reducing risk.")
        
    if clinical_data and clinical_data.get("reasons"):
        reasons.extend(clinical_data["reasons"])
        
    return {
        "analysis_level": "High Risk" if score > 0.65 else ("Medium Risk" if score > 0.35 else "Low Risk"),
        "reasons": reasons,
        "recommendation": "Emergency neurological consult required." if score > 0.65 else "Monitor speech patterns.",
        "confidence_score": 0.85
    }

def predict_stroke_type(face_score: float, speech_score: float) -> Dict[str, Any]:
    """
    Predicts the potential stroke type (simulation).
    """
    avg_score = (face_score + speech_score) / 2
    
    if avg_score > 0.75:
        stroke_type = "Potential Hemorrhagic Stroke"
        pathophysiology = "Bleeding into brain tissue; requires rapid neurosurgical consult."
        confidence = 0.65
    else:
        stroke_type = "Potential Ischemic Stroke"
        pathophysiology = "Blood clot blocking oxygen; potentially eligible for tPA (clot-buster)."
        confidence = 0.82
        
    return {
        "type": stroke_type,
        "pathophysiology": pathophysiology,
        "confidence": confidence,
        "warning": "Stroke type must be confirmed via non-contrast CT head scan."
    }
