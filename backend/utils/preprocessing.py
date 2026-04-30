"""
backend/utils/preprocessing.py

Centralized preprocessing utilities for the Multi-Modal Stroke Detection system.
Handles image loading/normalization and audio loading for both face and speech pipelines.

Sources inspired by:
- vinayadusumilli/Multimodal-Emotion-AI  (face + audio pipeline design)
- purnima99/EmotionDetection             (librosa audio loading pattern)
"""

import io
import logging
from typing import Tuple

import cv2
import librosa
import numpy as np

# ── Logger ────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
IMAGE_TARGET_SIZE = (224, 224)   # Standard CNN input size (VGG/ResNet style)
AUDIO_SAMPLE_RATE = 22050        # librosa default; RAVDESS recordings are 48 kHz but
                                  # we resample to 22050 for consistent MFCC extraction


# ═══════════════════════════════════════════════════════════════════════════════
#  IMAGE PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def load_image(file_bytes: bytes) -> np.ndarray:
    """
    Load image from raw bytes and convert to an OpenCV BGR numpy array.

    Args:
        file_bytes: Raw bytes of the uploaded image (JPEG, PNG, BMP, etc.)

    Returns:
        BGR numpy array of shape (H, W, 3) as uint8.

    Raises:
        ValueError: If the bytes cannot be decoded as a valid image.
    """
    try:
        # Decode via numpy buffer → OpenCV (supports JPEG, PNG, BMP, TIFF, WebP)
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image from provided bytes. Ensure the file is a valid JPEG, PNG, BMP, or WebP image.")

        logger.debug("Image loaded: shape=%s, dtype=%s", img.shape, img.dtype)
        return img

    except Exception as exc:
        logger.error("Image loading failed: %s", exc)
        raise ValueError(f"Invalid image data: {exc}") from exc


def resize_image(img: np.ndarray, target_size: Tuple[int, int] = IMAGE_TARGET_SIZE) -> np.ndarray:
    """
    Resize image to target_size using Lanczos interpolation.

    Args:
        img: BGR numpy array.
        target_size: (width, height) tuple.

    Returns:
        Resized BGR numpy array.
    """
    return cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)


def normalize_image(img: np.ndarray) -> np.ndarray:
    """
    Normalize a BGR image to float32 in range [0, 1] using ImageNet-style
    mean subtraction and standard deviation scaling.

    Pipeline:
        1. Convert BGR → RGB
        2. Cast to float32, divide by 255
        3. Subtract ImageNet channel means [0.485, 0.456, 0.406]
        4. Divide by ImageNet channel stds  [0.229, 0.224, 0.225]

    Args:
        img: BGR uint8 numpy array.

    Returns:
        Normalized float32 numpy array of same shape.
    """
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    normalized = (rgb - mean) / std
    return normalized


def preprocess_image_for_cnn(file_bytes: bytes) -> np.ndarray:
    """
    Full image preprocessing pipeline:  bytes → CNN-ready float32 array.

    Returns:
        Array of shape (1, 224, 224, 3) — batch dimension included, ready for
        model.predict().
    """
    img       = load_image(file_bytes)
    img       = resize_image(img, IMAGE_TARGET_SIZE)
    img_norm  = normalize_image(img)
    batch     = np.expand_dims(img_norm, axis=0)   # shape: (1, 224, 224, 3)
    return batch


# ═══════════════════════════════════════════════════════════════════════════════
#  AUDIO PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def load_audio(file_bytes: bytes, sr: int = AUDIO_SAMPLE_RATE) -> Tuple[np.ndarray, int]:
    """
    Load audio from raw bytes using librosa.

    Supports WAV, MP3, OGG, FLAC (via soundfile/audioread under the hood).
    Audio is resampled to `sr` and converted to mono.

    Args:
        file_bytes: Raw bytes of the uploaded audio file.
        sr:         Target sample rate (default 22050 Hz).

    Returns:
        Tuple (y, sr) where y is a float32 mono waveform numpy array.

    Raises:
        ValueError: If the audio cannot be decoded.
    """
    try:
        audio_buffer = io.BytesIO(file_bytes)
        y, actual_sr = librosa.load(audio_buffer, sr=sr, mono=True)
        logger.debug("Audio loaded: samples=%d, sr=%d", len(y), actual_sr)
        return y, actual_sr

    except Exception as exc:
        logger.error("Audio loading failed: %s", exc)
        raise ValueError(f"Invalid audio data: {exc}") from exc


def pad_or_trim_audio(y: np.ndarray, target_length: int = AUDIO_SAMPLE_RATE * 3) -> np.ndarray:
    """
    Ensure the audio waveform is exactly `target_length` samples.
    - If shorter: zero-pad on the right.
    - If longer:  trim from the start (first N samples).

    Default target is 3 seconds @ 22050 Hz = 66150 samples.
    """
    if len(y) < target_length:
        pad = target_length - len(y)
        y = np.pad(y, (0, pad), mode="constant")
    else:
        y = y[:target_length]
    return y
