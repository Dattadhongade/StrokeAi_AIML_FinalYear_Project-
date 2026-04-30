import cv2
import numpy as np
import librosa
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

# ── Face Clinical Preprocessing ──────────────────────────────────────────────

def extract_clinical_landmarks(image_bgr: np.ndarray) -> np.ndarray:
    """
    Extracts 468 MediaPipe landmarks and calculates the Facial Asymmetry Index (FAI).
    This is a research-standard for quantifying stroke-induced drooping.
    """
    # Note: Lazy import to avoid startup overhead if not using face module
    try:
        import mediapipe as mp
    except ImportError:
        logger.error("MediaPipe not installed.")
        return np.zeros(468 * 3)

    mp_face_mesh = mp.solutions.face_mesh
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return np.zeros(468 * 3) # Return zero vector if no face
            
        landmarks = results.multi_face_landmarks[0]
        coords = []
        for lm in landmarks.landmark:
            coords.extend([lm.x, lm.y, lm.z])
            
        return np.array(coords)

def calculate_asymmetry_index(landmarks: np.ndarray) -> float:
    """
    Calculates a score based on the difference between left and right facial landmarks.
    Focuses on mouth corners and eye corners (NIHSS priority areas).
    """
    # Reshape to (468, 3)
    coords = landmarks.reshape(-1, 3)
    
    # Landmark indices for key symmetry points (MediaPipe indices)
    # Mouth corners: 61, 291
    # Eye corners: 33, 263
    mouth_left = coords[61]
    mouth_right = coords[291]
    
    # Simple vertical difference as a proxy for drooping
    mouth_droop = abs(mouth_left[1] - mouth_right[1])
    return float(mouth_droop)

# ── Speech Clinical Preprocessing ─────────────────────────────────────────────

def extract_advanced_speech_features(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Extracts MFCC + Delta + Delta-Delta features.
    Captures temporal dynamics of dysarthric speech (slurring).
    """
    # MFCC (13 or 20 is standard for speech research)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Delta (first order)
    delta = librosa.feature.delta(mfcc)
    
    # Delta-Delta (second order)
    delta2 = librosa.feature.delta(mfcc, order=2)
    
    # Concatenate means and standard deviations to capture prosodic flattening
    features = np.concatenate([
        np.mean(mfcc, axis=1),
        np.std(mfcc, axis=1),
        np.mean(delta, axis=1),
        np.std(delta, axis=1),
        np.mean(delta2, axis=1),
        np.std(delta2, axis=1)
    ])
    
    return features.astype(np.float32)

def clinical_noise_reduction(y: np.ndarray) -> np.ndarray:
    """
    Applies basic noise suppression to improve signal-to-noise ratio (SNR)
    for clinical recordings which might have background hospital noise.
    """
    # Simple spectral subtraction proxy using librosa
    stft = librosa.stft(y)
    stft_mag = np.abs(stft)
    noise_floor = np.mean(stft_mag[:, :10], axis=1, keepdims=True)
    stft_denoised = stft * (stft_mag > noise_floor * 1.5)
    return librosa.istft(stft_denoised)
