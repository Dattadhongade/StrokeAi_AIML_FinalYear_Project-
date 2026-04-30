import os
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple

import cv2
import numpy as np
from sklearn.model_selection import train_test_split

# Local imports
from .preprocessing import extract_clinical_landmarks, extract_advanced_speech_features, clinical_noise_reduction
from .augmentation import augment_face_clinical, augment_speech_clinical

logger = logging.getLogger(__name__)

class ClinicalDatasetModule:
    """
    Production-ready module for handling clinical datasets for stroke detection.
    Supports structured schemas, validation, and batch loading.
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / "metadata.json"
        self.face_dir = self.base_path / "clinical_face"
        self.speech_dir = self.base_path / "clinical_speech"
        
        # Ensure directories exist
        self.face_dir.mkdir(parents=True, exist_ok=True)
        self.speech_dir.mkdir(parents=True, exist_ok=True)

    def _save_metadata(self, data: Dict[str, Any]):
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=4)

    def validate_dataset(self, module_type: str = "face"):
        """
        Validates the dataset for missing files or corrupted data.
        """
        target_dir = self.face_dir if module_type == "face" else self.speech_dir
        files = list(target_dir.rglob("*.*"))
        
        report = {
            "total_files": len(files),
            "corrupted": 0,
            "classes": {}
        }
        
        for f in files:
            label = f.parent.name
            report["classes"][label] = report["classes"].get(label, 0) + 1
            # Basic corruption check
            if module_type == "face":
                if cv2.imread(str(f)) is None:
                    report["corrupted"] += 1
        
        return report

    def load_face_dataset(self, augment: bool = False) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Loads clinical face dataset, performs preprocessing, and returns X, y.
        """
        X, y = [], []
        labels_map = {"normal": 0, "stroke": 1}
        
        for label_name, label_idx in labels_map.items():
            class_dir = self.face_dir / label_name
            if not class_dir.exists(): continue
            
            for img_path in class_dir.glob("*.jpg"):
                img = cv2.imread(str(img_path))
                if img is None: continue
                
                if augment:
                    img = augment_face_clinical(img)
                
                landmarks = extract_clinical_landmarks(img)
                X.append(landmarks)
                y.append(label_idx)
        
        return np.array(X), np.array(y), labels_map

    def load_speech_dataset(self, augment: bool = False) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Loads dysarthria speech dataset (e.g. TORGO structure), performs preprocessing, and returns X, y.
        """
        X, y = [], []
        labels_map = {"normal": 0, "dysarthria": 1}
        
        for label_name, label_idx in labels_map.items():
            class_dir = self.speech_dir / label_name
            if not class_dir.exists(): continue
            
            for audio_path in class_dir.glob("*.wav"):
                import librosa
                try:
                    y_audio, sr = librosa.load(str(audio_path), sr=22050)
                    y_audio = clinical_noise_reduction(y_audio)
                    
                    if augment:
                        y_audio = augment_speech_clinical(y_audio, sr)
                    
                    features = extract_advanced_speech_features(y_audio, sr)
                    X.append(features)
                    y.append(label_idx)
                except Exception as e:
                    logger.error(f"Error loading {audio_path}: {e}")
        
        return np.array(X), np.array(y), labels_map

# Reusable API
def get_clinical_loader(base_path: str):
    return ClinicalDatasetModule(base_path)
