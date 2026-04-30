# ⚕️ StrokeAI — Multi-Modal Stroke Risk Detection Framework

> **Final Year AI Project** — A high-performance, production-ready AI system that integrates facial asymmetry analysis, speech abnormality detection, and Generative AI for early stroke risk assessment.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB?logo=react)](https://react.dev)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-1.5_Flash-purple?logo=google-gemini)](https://aistudio.google.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.6+-orange?logo=scikit-learn)](https://scikit-learn.org)

---

## 🧠 Project Architecture

This framework implements the **FAST (Face, Arms, Speech, Time)** screening criteria using real-world trained machine learning models and state-of-the-art Generative AI.

| Module | Engine | algorithm / LLM | Feature Vector |
|:---|:---|:---|:---|
| **Face Analysis** | **OpenCV + CNN** | MLP Classifier | 16-dim symmetry + edge gradient mappings |
| **Speech Analysis** | **Librosa + LSTM** | MLP Classifier | 122-dim MFCC / Delta / Delta-Delta |
| **Fusion Engine** | **Weighted Model** | Clinical Fusion | `0.6 × Face + 0.4 × Speech` |
| **Smart Chatbot** | **Google Gemini** | LLM (1.5 Flash) | Context-aware medical knowledge base |

---

## 🔥 Key Features

- **📸 Multi-Modal Analysis**: Real-time webcam capture and audio recording for dual-factor risk assessment.
- **🤖 Gemini AI Chatbot**: A smart assistant that explains results, provides medical FAQs, and offers emergency guidance based on your specific analysis scores.
- **⚠️ Emergency Detection**: Automated system that flags high-risk results and provides immediate FAST guidance.
- **☁️ Premium React UI**: Modern glassmorphism dashboard built with **React 19**, **Tailwind CSS**, and **Framer Motion**.
- **📦 Auto-Training Pipeline**: Integrated scripts to download professional datasets (LFW/RAVDESS) and train models locally.
- **🏥 Clinical Alignment**: Recommendations and risk bands calibrated against NIHSS stroke severity guidelines.

---

## 🚀 Quick Start (Running the App)

### 1. Setup Environment
```powershell
# Clone the repository
git clone <your-repo-url>
cd "stroke-ai-project"

# Backend setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

### 2. Configure AI (Optional but Recommended)
To enable the **"Unlimited" Medical Brain** (Gemini AI):
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

### 3. Launch the Application
**Terminal 1 (Backend):**
```powershell
python -m uvicorn backend.app:app --port 8000 --reload
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

- **App URL:** [http://localhost:5173](http://localhost:5173)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Technical Methodology

### Facial Asymmetry (Module 1)
Stroke-induced hemiparesis often causes "face drooping" on one side. 
- **Geometric Mapping**: Computes centroid positions of eyes/mouth to detect tilts.
- **Symmetry Deviation**: Mirrors the face and computes mathematical differences in pixel intensity and edge density.
- **Classification**: An MLP classifier determines if asymmetry matches stroke patterns.

### Speech Abnormality (Module 2)
Dysarthria (slurred speech) is detected through prosodic shifts.
- **MFCC Extraction**: Converts raw audio into frequency domain features to isolate articulation abnormalities.
- **Emotion Profiling**: Detects vocal strain and pitch-shifts characteristic of acute slurring.

### Generative AI Integration (Module 3)
The system uses **Google Gemini 1.5 Flash** to:
1. **Interpret Results**: Explain *why* a risk is high (e.g., "High asymmetry detected in left quadrant").
2. **Medical KB**: Provide detailed information on stroke types, medications (Aspirin, Statins), and hospital procedures.

---

## 📂 Project Structure

```text
stroke-ai-project/
├── frontend/             # React (Vite) Application
│   ├── src/components/   # Modular UI (Chatbot, FusionModule, etc.)
│   ├── src/pages/        # Dashboard & Analysis views
│   └── tailwind.config.js # Premium styling configuration
├── backend/              # FastAPI Application
│   ├── app.py            # Server & Middleware entry point
│   ├── routes/           # face.py, speech.py, fusion.py, chatbot.py
│   ├── models/           # Real ML Weight files (.pkl)
│   └── utils/            # Image/Audio preprocessing logic
├── .env                  # API Keys & Configuration
├── requirements.txt      # Python dependencies
└── download_and_train.py # Dataset download & training master script
```

---

## ⚠️ Medical Disclaimer

This application is a **research demonstration** for academic purposes only. It is **NOT** a certified medical device and should **NOT** be used as a substitute for professional medical diagnosis. Always consult a qualified physician for medical advice.

---

## 👥 Contributors
Final Year Project — **Multi-Modal AI Framework for Early Stroke Detection**
*Built with: FastAPI · React · Gemini AI · OpenCV · Librosa · Scikit-Learn*
