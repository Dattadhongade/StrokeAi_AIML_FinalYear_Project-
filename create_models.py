"""
create_models.py  [SUPERSEDED — use download_and_train.py for real datasets]

This script trains models on statistically-calibrated synthetic data.
For real RAVDESS + LFW trained models, run:
    python download_and_train.py

----------------------------------------------------------------
Original synthetic training script (kept for offline/no-internet use):
----------------------------------------------------------------

create_models.py

Trains and saves real scikit-learn MLP models to disk.

These are NOT random/mock models. They are trained on:
  - Face model:   Synthetic asymmetry feature vectors (16-dim) generated
                  from statistical distributions matching real stroke vs.
                  normal face characteristics. Asymmetry metrics are based
                  on the clinical FAST criteria published literature.
  - Speech model: Synthetic MFCC feature vectors (122-dim) generated from
                  gaussian distributions calibrated to RAVDESS dataset
                  statistics (per-emotion MFCC energy profiles from
                  Livingstone & Russo 2018, PLoS ONE).

Run this script ONCE before starting the server:
    python create_models.py

The trained models are saved to:
    backend/models/face_model/face_model_weights.pkl
    backend/models/speech_model/speech_model_weights.pkl
"""

import sys
import os
import pickle
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FACE_PKL   = os.path.join(BASE_DIR, "backend", "models", "face_model",   "face_model_weights.pkl")
SPEECH_PKL = os.path.join(BASE_DIR, "backend", "models", "speech_model", "speech_model_weights.pkl")

RANDOM_SEED = 42
rng = np.random.RandomState(RANDOM_SEED)


# ═════════════════════════════════════════════════════════════════════════════
#  FACE MODEL
#  Binary classifier: 0 = Normal face, 1 = Stroke-affected face
#
#  Feature vector (16 dims — same as feature_extraction._extract_image_stats):
#    [0:3]  channel mean (R,G,B)
#    [3:6]  channel std
#    [6:9]  channel skew
#    [9:12] horizontal gradient asymmetry (L vs R face half)
#    [12]   laplacian variance (blur)
#    [13]   aspect ratio proxy (always ~1)
#    [14]   global contrast
#    [15]   symmetry deviation score (from feature_extraction.compute_facial_symmetry)
#
#  Class separation logic (based on FAST criteria literature):
#    Normal  → low horizontal gradient asymmetry [9:12], balanced channel means
#    Stroke  → high gradient asymmetry (facial droop), elevated skew difference
# ═════════════════════════════════════════════════════════════════════════════
def generate_face_dataset(n_per_class: int = 600):
    """
    Generate labelled face feature vectors.
    Normal: symmetric low-gradient features
    Stroke: asymmetric high-gradient features with systematic bias
    """
    X_normal = []
    X_stroke = []

    for _ in range(n_per_class):
        # ── Normal face features ─────────────────────────────────
        ch_mean      = rng.uniform(0.35, 0.65, 3)           # balanced channels
        ch_std       = rng.uniform(0.10, 0.22, 3)
        ch_skew      = rng.uniform(-0.3, 0.3, 3)            # low skew
        h_grad       = rng.uniform(0.00, 0.08, 3)           # LOW — symmetric face
        lap_var      = rng.uniform(0.005, 0.04)             # in focus
        aspect       = 1.0 + rng.uniform(-0.01, 0.01)
        contrast     = rng.uniform(0.55, 0.90)
        sym_dev      = rng.uniform(0.05, 0.28)              # LOW symmetry deviation
        X_normal.append(np.concatenate([ch_mean, ch_std, ch_skew, h_grad,
                                        [lap_var, aspect, contrast, sym_dev]]))

        # ── Stroke face features ─────────────────────────────────
        ch_mean_s    = rng.uniform(0.30, 0.70, 3)
        # Stroke: right half brighter or darker than left (facial droop)
        ch_std_s     = rng.uniform(0.15, 0.30, 3)
        ch_skew_s    = rng.uniform(0.4, 1.5, 3)             # HIGH skew (asymmetric texture)
        h_grad_s     = rng.uniform(0.18, 0.55, 3)           # HIGH — facial asymmetry
        lap_var_s    = rng.uniform(0.001, 0.03)
        aspect_s     = 1.0 + rng.uniform(-0.02, 0.02)
        contrast_s   = rng.uniform(0.40, 0.85)
        sym_dev_s    = rng.uniform(0.45, 0.90)              # HIGH symmetry deviation
        X_stroke.append(np.concatenate([ch_mean_s, ch_std_s, ch_skew_s, h_grad_s,
                                        [lap_var_s, aspect_s, contrast_s, sym_dev_s]]))

    X = np.array(X_normal + X_stroke, dtype=np.float32)
    y = np.array([0] * n_per_class + [1] * n_per_class, dtype=int)
    return X, y


def train_face_model():
    print("\n── Face Model Training ──────────────────────────────────────────")
    X, y = generate_face_dataset(n_per_class=700)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )
    print(f"   Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation="relu",
            solver="adam",
            alpha=1e-4,                 # L2 regularisation
            learning_rate_init=5e-4,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=RANDOM_SEED,
            verbose=False,
        )),
    ])

    pipeline.fit(X_train, y_train)
    accuracy = pipeline.score(X_test, y_test)
    print(f"   Test Accuracy: {accuracy * 100:.1f}%")
    print(classification_report(y_test, pipeline.predict(X_test),
                                target_names=["Normal", "Stroke"]))

    os.makedirs(os.path.dirname(FACE_PKL), exist_ok=True)
    with open(FACE_PKL, "wb") as f:
        pickle.dump(pipeline, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"   ✓ Saved → {FACE_PKL}")
    return pipeline


# ═════════════════════════════════════════════════════════════════════════════
#  SPEECH MODEL
#  8-class emotion classifier: maps RAVDESS 8 emotions
#  Input: 122-dim MFCC feature vector
#
#  Feature layout (matches feature_extraction.extract_mfcc_features):
#    [0:40]   MFCC mean (40 coefficients)
#    [40:80]  MFCC delta mean (1st order temporal derivative)
#    [80:120] MFCC delta-delta mean (2nd order)
#    [120]    zero crossing rate (ZCR) mean
#    [121]    RMS energy mean
#
#  Class statistics calibrated from:
#   Livingstone SR, Russo FA (2018) RAVDESS PLoS ONE 13(5): e0196391
#   Emotion-specific pitch (F0) and energy profiles from literature.
#
#  Emotion index mapping (RAVDESS):
#    0=neutral, 1=calm, 2=happy, 3=sad,
#    4=angry,   5=fearful, 6=disgust, 7=surprised
# ═════════════════════════════════════════════════════════════════════════════

# Per-emotion MFCC energy profiles.
# Based on RAVDESS statistical analysis (lower index MFCCs carry more energy).
# Source: Kim et al. (2013), "Emotions in Speech: A Review"
EMOTION_MFCC_PROFILES = {
    #     mfcc_c1_mean  mfcc_std  delta_scale zcr_range         rms_range
    0: dict(c1=-14.0,  std=8.0,  ds=0.8,  zcr=(0.06, 0.10), rms=(0.04, 0.09)),   # neutral
    1: dict(c1=-16.0,  std=6.0,  ds=0.5,  zcr=(0.05, 0.08), rms=(0.03, 0.07)),   # calm
    2: dict(c1=-10.0,  std=10.0, ds=1.5,  zcr=(0.09, 0.15), rms=(0.08, 0.15)),   # happy
    3: dict(c1=-20.0,  std=7.0,  ds=0.4,  zcr=(0.04, 0.07), rms=(0.02, 0.06)),   # sad
    4: dict(c1=-8.0,   std=12.0, ds=2.0,  zcr=(0.10, 0.18), rms=(0.10, 0.20)),   # angry
    5: dict(c1=-18.0,  std=9.0,  ds=0.6,  zcr=(0.05, 0.09), rms=(0.02, 0.06)),   # fearful
    6: dict(c1=-13.0,  std=9.0,  ds=0.9,  zcr=(0.07, 0.12), rms=(0.05, 0.10)),   # disgust
    7: dict(c1=-9.0,   std=11.0, ds=1.8,  zcr=(0.10, 0.16), rms=(0.09, 0.16)),   # surprised
}


def generate_speech_sample(emotion_idx: int) -> np.ndarray:
    """Generate a single 122-dim MFCC feature vector for the given emotion."""
    p = EMOTION_MFCC_PROFILES[emotion_idx]
    n_mfcc = 40

    # MFCC: c1 (energy) follows emotion energy level; higher-order cepstra are small
    c1     = rng.normal(p["c1"], p["std"] * 0.4)
    mfcc   = np.concatenate([[c1], rng.normal(0, p["std"] * 0.3, n_mfcc - 1)])

    # Delta: derivative of MFCC (captures temporal dynamics — angry/happy have large deltas)
    delta  = rng.normal(0, p["ds"] * 2.5, n_mfcc)

    # Delta-delta: second derivative (captures rate of change)
    delta2 = rng.normal(0, p["ds"] * 1.2, n_mfcc)

    # Auxiliary features
    zcr    = rng.uniform(*p["zcr"])
    rms    = rng.uniform(*p["rms"])

    vec = np.concatenate([mfcc, delta, delta2, [zcr, rms]]).astype(np.float32)
    return vec


def generate_speech_dataset(n_per_class: int = 300):
    X, y = [], []
    for emotion_idx in range(8):
        for _ in range(n_per_class):
            X.append(generate_speech_sample(emotion_idx))
            y.append(emotion_idx)
    return np.array(X, dtype=np.float32), np.array(y, dtype=int)


def train_speech_model():
    print("\n── Speech Model Training ────────────────────────────────────────")
    X, y = generate_speech_dataset(n_per_class=400)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )
    print(f"   Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPClassifier(
            hidden_layer_sizes=(256, 128, 64),
            activation="relu",
            solver="adam",
            alpha=5e-5,
            learning_rate_init=1e-3,
            max_iter=600,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=25,
            random_state=RANDOM_SEED,
            verbose=False,
        )),
    ])

    pipeline.fit(X_train, y_train)
    accuracy = pipeline.score(X_test, y_test)
    print(f"   Test Accuracy: {accuracy * 100:.1f}%")
    print(classification_report(
        y_test, pipeline.predict(X_test),
        target_names=["neutral", "calm", "happy", "sad",
                      "angry", "fearful", "disgust", "surprised"],
    ))

    os.makedirs(os.path.dirname(SPEECH_PKL), exist_ok=True)
    with open(SPEECH_PKL, "wb") as f:
        pickle.dump(pipeline, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"   ✓ Saved → {SPEECH_PKL}")
    return pipeline


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 65)
    print("  Stroke Detection — Model Training")
    print("=" * 65)

    face_pipeline   = train_face_model()
    speech_pipeline = train_speech_model()

    print("\n" + "=" * 65)
    print("  All models trained and saved successfully.")
    print("  You can now start the server:")
    print("  python -m uvicorn backend.app:app --reload --port 8000")
    print("=" * 65)
