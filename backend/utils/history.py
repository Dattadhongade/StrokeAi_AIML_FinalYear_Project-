"""
backend/utils/history.py

Manages patient analysis history and trend tracking.
Stores data in a local JSON file for persistent demo purposes.
"""

import json
import os
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "data" / "history.json"

def ensure_history_exists():
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

def save_analysis(result):
    ensure_history_exists()
    
    # Add timestamp
    result['timestamp'] = datetime.now().isoformat()
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        history.append(result)
        
        # Keep only last 10 for demo
        history = history[-10:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def get_history():
    ensure_history_exists()
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def get_trends():
    history = get_history()
    if not history:
        return []
    
    trends = []
    for entry in history:
        trends.append({
            "date": entry['timestamp'][:10],
            "score": entry.get('final_score', entry.get('face_risk_score', 0))
        })
    return trends
