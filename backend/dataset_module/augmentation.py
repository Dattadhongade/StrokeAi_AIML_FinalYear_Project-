import cv2
import numpy as np
import librosa
import random

# ── Face Augmentation ────────────────────────────────────────────────────────

def augment_face_clinical(image: np.ndarray) -> np.ndarray:
    """
    Augments face images to simulate real-world clinical conditions
    (poor lighting, camera angles in ER).
    """
    # Random brightness/contrast
    alpha = random.uniform(0.8, 1.2)
    beta = random.randint(-20, 20)
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    # Random rotation (mild, simulating head tilt)
    h, w = image.shape[:2]
    angle = random.uniform(-10, 10)
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    
    return image

# ── Speech Augmentation ──────────────────────────────────────────────────────

def augment_speech_clinical(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Augments speech samples to simulate different voice pitches 
    and background clinical noise.
    """
    # Pitch shift
    steps = random.uniform(-2, 2)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
    
    # Random noise injection
    noise_amp = 0.005 * np.random.uniform() * np.amax(y_shifted)
    y_noise = y_shifted + noise_amp * np.random.normal(size=y_shifted.shape)
    
    return y_noise.astype(np.float32)
