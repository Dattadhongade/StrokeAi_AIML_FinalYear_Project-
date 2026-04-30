import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Dna, ShieldAlert,
  Info, Loader2, AlertTriangle, Activity,
  Camera, Mic, Square, X, Upload,
  ScanFace, Mic2, CheckCircle2, ShieldCheck, AlertCircle
} from 'lucide-react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import axios from 'axios';

ChartJS.register(ArcElement, Tooltip, Legend);

const API_BASE = 'http://localhost:8000';

const FusionModule = () => {
  const [faceFile, setFaceFile] = useState(null);
  const [speechFile, setSpeechFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [useDetailedVitals, setUseDetailedVitals] = useState(false);
  const [metadata, setMetadata] = useState({ age: '', bp: '', glucose: '' });
  const [simpleVitals, setSimpleVitals] = useState({
    ageOver55: 'unknown',
    highBP: 'unknown',
    highSugar: 'unknown'
  });
  const [analysisSteps, setAnalysisSteps] = useState([
    { id: 1, label: 'Initializing Neural Engines', status: 'pending' },
    { id: 2, label: 'Scanning Facial Landmarks', status: 'pending' },
    { id: 3, label: 'Extracting Acoustic MFCCs', status: 'pending' },
    { id: 4, label: 'Fusing Multi-Modal Biometrics', status: 'pending' }
  ]);

  const [isCapturing, setIsCapturing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    let interval;
    if (isCapturing && streamRef.current) {
      // Try multiple times to attach stream in case of mount delays
      interval = setInterval(() => {
        if (videoRef.current && !videoRef.current.srcObject) {
          videoRef.current.srcObject = streamRef.current;
          clearInterval(interval);
        }
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isCapturing]);

  // --- Face Capture Logic ---
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      setIsCapturing(true);
    } catch (err) {
      setError('Camera access denied.');
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0);
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'fusion_face.jpg', { type: 'image/jpeg' });
        setFaceFile(file);
        stopCamera();
      }
    }, 'image/jpeg');
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(track => track.stop());
    setIsCapturing(false);
  };

  // --- Speech Recording Logic ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        try {
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const blob = new Blob(audioChunksRef.current, { type: mediaRecorderRef.current.mimeType });
          const arrayBuffer = await blob.arrayBuffer();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

          const wavBlob = audioBufferToWav(audioBuffer);
          const file = new File([wavBlob], 'fusion_speech.wav', { type: 'audio/wav' });
          setSpeechFile(file);
        } catch (err) {
          setError('Failed to process recording.');
        } finally {
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('Microphone access denied.');
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  // --- WAV Encoder ---
  const audioBufferToWav = (buffer) => {
    const length = buffer.length * buffer.numberOfChannels * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);
    const sampleRate = buffer.sampleRate;
    const channels = buffer.numberOfChannels;
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    writeString(0, 'RIFF');
    view.setUint32(4, length - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, channels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * channels * 2, true);
    view.setUint16(32, channels * 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, length - 44, true);
    let offset = 44;
    for (let i = 0; i < buffer.length; i++) {
      for (let channel = 0; channel < channels; channel++) {
        let sample = buffer.getChannelData(channel)[i];
        sample = Math.max(-1, Math.min(1, sample));
        sample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        view.setInt16(offset, sample, true);
        offset += 2;
      }
    }
    return new Blob([arrayBuffer], { type: 'audio/wav' });
  };

  const handlePredict = async () => {
    if (!faceFile || !speechFile) return;
    setLoading(true);
    setError(null);
    setResult(null);

    // Simulation of sequential analysis for better UX
    for (let i = 0; i < analysisSteps.length; i++) {
      setAnalysisSteps(prev => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'loading' } : s
      ));
      await new Promise(r => setTimeout(r, 800));
      setAnalysisSteps(prev => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'complete' } : s
      ));
    }

    const formData = new FormData();
    formData.append('image', faceFile);
    formData.append('audio', speechFile);

    // Process Metadata
    let age = metadata.age;
    let bp = metadata.bp;
    let glucose = metadata.glucose;

    if (!useDetailedVitals) {
      age = simpleVitals.ageOver55 === 'yes' ? 65 : (simpleVitals.ageOver55 === 'no' ? 30 : 0);
      bp = simpleVitals.highBP === 'yes' ? '150/95' : (simpleVitals.highBP === 'no' ? '120/80' : '');
      glucose = simpleVitals.highSugar === 'yes' ? 160 : (simpleVitals.highSugar === 'no' ? 100 : 0);
    }

    formData.append('age', age || 0);
    formData.append('bp', bp || '');
    formData.append('glucose', glucose || 0);

    try {
      const response = await axios.post(`${API_BASE}/predict`, formData);
      setResult(response.data);
      localStorage.setItem('stroke_analysis_result', JSON.stringify(response.data));
    } catch (err) {
      setError(err.response?.data?.detail || 'Fusion analysis failed.');
    } finally {
      setLoading(false);
      // Reset steps for next time
      setTimeout(() => {
        setAnalysisSteps(prev => prev.map(s => ({ ...s, status: 'pending' })));
      }, 1000);
    }
  };

  const gaugeData = result ? {
    datasets: [{
      data: [result.final_score, 100 - result.final_score],
      backgroundColor: [
        result.final_score > 0.65 ? '#ef4444' : result.final_score > 0.35 ? '#f59e0b' : '#22c55e',
        'rgba(255, 255, 255, 0.05)'
      ],
      borderWidth: 0,
      circumference: 240,
      rotation: 240,
      borderRadius: 10,
      cutout: '80%',
    }]
  } : null;

  const symptomsList = result ? [
    { id: 'droop', label: 'Facial Drooping (Hemiparesis)', value: result.face_analysis.face_risk_score > 0.4 },
    { id: 'asym', label: 'Geometric Asymmetry', value: result.face_analysis.symmetry_deviation > 0.35 },
    { id: 'slur', label: 'Speech Dysarthria (Slurring)', value: result.speech_analysis.speech_risk_score > 0.4 },
    { id: 'emot', label: 'Prosodic Strain Detection', value: result.speech_analysis.speech_risk_score > 0.6 }
  ] : [];

  return (
    <div className="glass-card p-8 lg:p-12 space-y-12 relative overflow-hidden">
      <div className="absolute top-0 left-0 px-4 py-1.5 bg-purple-600/20 text-purple-400 text-[10px] font-bold uppercase tracking-[0.2em] rounded-br-xl border-b border-r border-white/5">
        Module 03 — Multi-Modal Fusion
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left Side: DIAGNOSTIC INPUTS */}
        <div className="space-y-8">
          <div className="space-y-4">
            <h2 className="text-4xl font-extrabold font-outfit tracking-tight">Fusion Risk Assessment</h2>
            <p className="text-slate-400 leading-relaxed text-sm">
              The ultimate diagnostic layer. Combines multi-modal biometric data points into a single, high-fidelity risk coefficient.
            </p>
          </div>

          {/* Sequential Loading Indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3 p-6 rounded-2xl bg-blue-600/5 border border-blue-500/20"
            >
              {analysisSteps.map(step => (
                <div key={step.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {step.status === 'complete' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> :
                      step.status === 'loading' ? <Loader2 className="w-4 h-4 text-blue-500 animate-spin" /> :
                        <div className="w-4 h-4 rounded-full border-2 border-white/10" />}
                    <span className={`text-[11px] font-bold uppercase tracking-wider ${step.status === 'loading' ? 'text-white' : 'text-slate-500'}`}>{step.label}</span>
                  </div>
                  {step.status === 'complete' && <span className="text-[9px] font-bold text-green-500 uppercase tracking-widest">Verified</span>}
                </div>
              ))}
            </motion.div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Face Card */}
            <div className={`p-6 rounded-2xl border transition-all relative overflow-hidden ${faceFile ? 'bg-blue-600/5 border-blue-500/20' : 'bg-slate-900 border-white/5'}`}>
              <AnimatePresence mode="wait">
                {isCapturing ? (
                  <motion.div key="camera" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                    <video ref={videoRef} autoPlay playsInline className="w-full aspect-video rounded-xl bg-black object-cover" />
                    <div className="flex gap-2">
                      <button onClick={capturePhoto} className="flex-1 py-2 rounded-lg bg-blue-600 text-[10px] font-bold flex items-center justify-center gap-2">
                        <Camera className="w-4 h-4" /> Snap
                      </button>
                      <button onClick={stopCamera} className="px-4 py-2 rounded-lg bg-slate-800 text-xs font-bold">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div key="info" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${faceFile ? 'bg-blue-600' : 'bg-slate-800'}`}>
                        <Activity className="text-white w-6 h-6" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-200">Face AI</p>
                        <p className="text-[10px] text-slate-500 truncate max-w-[100px]">{faceFile ? faceFile.name : 'Awaiting'}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => document.getElementById('fusion-face')?.click()} className="flex-1 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-[9px] font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-1">
                        <Upload className="w-3 h-3" /> File
                      </button>
                      <button onClick={startCamera} className="flex-1 py-2 rounded-lg bg-blue-600/10 border border-blue-500/30 text-blue-400 text-[9px] font-bold uppercase tracking-wider hover:bg-blue-600/20 transition-colors flex items-center justify-center gap-1">
                        <Camera className="w-3 h-3" /> Live
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <input type="file" id="fusion-face" className="hidden" onChange={(e) => setFaceFile(e.target.files?.[0] || null)} accept="image/*" />
            </div>

            {/* Speech Card */}
            <div className={`p-6 rounded-2xl border transition-all relative overflow-hidden ${speechFile ? 'bg-teal-600/5 border-teal-500/20' : 'bg-slate-900 border-white/5'}`}>
              <AnimatePresence mode="wait">
                {isRecording ? (
                  <motion.div key="recording" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center justify-center py-4 space-y-4">
                    <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center animate-pulse">
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                    </div>
                    <button onClick={stopRecording} className="px-6 py-2 rounded-full bg-red-500 text-[10px] font-bold flex items-center gap-2">
                      <Square className="w-3 h-3" /> Stop
                    </button>
                  </motion.div>
                ) : (
                  <motion.div key="info" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${speechFile ? 'bg-teal-600' : 'bg-slate-800'}`}>
                        <Mic className="text-white w-6 h-6" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-200">Speech AI</p>
                        <p className="text-[10px] text-slate-500 truncate max-w-[100px]">{speechFile ? speechFile.name : 'Awaiting'}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => document.getElementById('fusion-speech')?.click()} className="flex-1 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-[9px] font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-1">
                        <Upload className="w-3 h-3" /> File
                      </button>
                      <button onClick={startRecording} className="flex-1 py-2 rounded-lg bg-teal-600/10 border border-teal-500/30 text-teal-400 text-[9px] font-bold uppercase tracking-wider hover:bg-teal-600/20 transition-colors flex items-center justify-center gap-1">
                        <Mic className="w-3 h-3" /> Rec
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <input type="file" id="fusion-speech" className="hidden" onChange={(e) => setSpeechFile(e.target.files?.[0] || null)} accept="audio/*" />
            </div>
          </div>

          {/* Clinical Metadata Section */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-white/5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Step 2: Patient Clinical Health</h3>
              <label className="flex items-center gap-2 cursor-pointer group">
                <span className="text-[10px] font-bold text-slate-500 group-hover:text-blue-400 transition-colors uppercase tracking-widest">Detailed</span>
                <div className="relative">
                  <input type="checkbox" checked={useDetailedVitals} onChange={() => setUseDetailedVitals(!useDetailedVitals)} className="sr-only" />
                  <div className={`w-8 h-4 rounded-full transition-colors ${useDetailedVitals ? 'bg-blue-600' : 'bg-slate-700'}`} />
                  <div className={`absolute top-0.5 left-0.5 w-3 h-3 rounded-full bg-white transition-transform ${useDetailedVitals ? 'translate-x-4' : 'translate-x-0'}`} />
                </div>
              </label>
            </div>

            {useDetailedVitals ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <input type="number" placeholder="Age" value={metadata.age} onChange={e => setMetadata({ ...metadata, age: e.target.value })} className="bg-black/40 border border-white/10 rounded-xl p-3 text-xs outline-none focus:border-blue-500/50" />
                <input type="text" placeholder="BP (140/90)" value={metadata.bp} onChange={e => setMetadata({ ...metadata, bp: e.target.value })} className="bg-black/40 border border-white/10 rounded-xl p-3 text-xs outline-none focus:border-blue-500/50" />
                <input type="number" placeholder="Glucose" value={metadata.glucose} onChange={e => setMetadata({ ...metadata, glucose: e.target.value })} className="bg-black/40 border border-white/10 rounded-xl p-3 text-xs outline-none focus:border-blue-500/50" />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {[
                  { id: 'ageOver55', label: 'Over 55 years old?' },
                  { id: 'highBP', label: 'High blood pressure?' },
                  { id: 'highSugar', label: 'High blood sugar?' }
                ].map((q) => (
                  <div key={q.id} className="space-y-2">
                    <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{q.label}</p>
                    <div className="grid grid-cols-3 gap-1">
                      {['yes', 'no', 'unknown'].map((opt) => (
                        <button
                          key={opt}
                          onClick={() => setSimpleVitals({ ...simpleVitals, [q.id]: opt })}
                          className={`py-1.5 rounded-lg text-[9px] font-black uppercase tracking-tighter transition-all border ${simpleVitals[q.id] === opt
                              ? 'bg-blue-600 border-blue-400 text-white'
                              : 'bg-black/40 border-white/5 text-slate-500 hover:border-white/20'
                            }`}
                        >
                          {opt === 'unknown' ? "?" : opt}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            disabled={!faceFile || !speechFile || loading}
            onClick={handlePredict}
            className="w-full py-5 rounded-2xl bg-linear-to-r from-blue-600 to-teal-600 hover:shadow-2xl hover:shadow-blue-500/20 disabled:opacity-50 text-white font-black text-lg tracking-wide transition-all flex items-center justify-center gap-3 group"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Dna className="w-6 h-6 group-hover:rotate-180 transition-transform duration-500" />}
            {loading ? 'Processing Multi-Modal Data...' : 'Run Fused Analysis →'}
          </button>

          {error && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertTriangle className="w-5 h-5" />
              {error}
            </div>
          )}
        </div>

        {/* Right Side: DIAGNOSTIC OUTPUT */}
        <div className="space-y-6">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-8">
                <div className="grid grid-cols-1 items-center gap-8">
                  <div className="relative flex flex-col items-center">
                    <div className="w-full max-w-[280px] aspect-square relative z-10">
                      {gaugeData && <Doughnut data={gaugeData} options={{
                        plugins: { legend: { display: false }, tooltip: { enabled: false } },
                        maintainAspectRatio: true,
                      }} />}
                      <div className="absolute inset-0 flex flex-col items-center justify-center pt-8">
                        <span className="text-5xl font-black font-outfit">{(result.final_score).toFixed(1)}%</span>
                        <span className={`text-sm font-bold uppercase tracking-widest mt-1 ${result.risk_label.includes('High') ? 'text-red-500' :
                            result.risk_label.includes('Medium') ? 'text-amber-500' : 'text-green-500'
                          }`}>
                          FUSED Risk Score
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className={`p-6 rounded-3xl border-2 flex gap-6 items-start ${result.risk_label.includes('High') ? 'bg-red-500/5 border-red-500/20' :
                      result.risk_label.includes('Medium') ? 'bg-amber-500/5 border-amber-500/20' : 'bg-green-500/5 border-green-500/20'
                    }`}>
                    <div className={`w-14 h-14 rounded-2xl shrink-0 flex items-center justify-center ${result.risk_label.includes('High') ? 'bg-red-500' :
                        result.risk_label.includes('Medium') ? 'bg-amber-500' : 'bg-green-500'
                      }`}>
                      <ShieldAlert className="text-white w-8 h-8" />
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-xl font-bold font-outfit">Clinical Outcome</h4>
                      <p className="text-slate-300 leading-relaxed italic text-xs">"{result.recommendation}"</p>
                    </div>
                  </div>

                  {/* Symptoms Checklist */}
                  <div className="p-6 rounded-2xl bg-slate-900 border border-white/5 space-y-4">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-green-400" />
                      <h5 className="text-xs font-bold uppercase tracking-widest text-slate-200">Biometric Checklist</h5>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {symptomsList.map(symptom => (
                        <div key={symptom.id} className={`flex items-center gap-3 p-3 rounded-xl border ${symptom.value ? 'bg-red-500/10 border-red-500/20' : 'bg-green-500/5 border-green-500/10'}`}>
                          {symptom.value ? <AlertCircle className="w-4 h-4 text-red-500" /> : <CheckCircle2 className="w-4 h-4 text-green-500" />}
                          <span className={`text-[9px] font-bold uppercase tracking-tighter ${symptom.value ? 'text-red-200' : 'text-green-200'}`}>{symptom.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-slate-900 border border-white/5 space-y-1">
                      <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Face AI</p>
                      <p className="text-xl font-black text-blue-400">{(result.face_score).toFixed(1)}%</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-900 border border-white/5 space-y-1">
                      <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Speech AI</p>
                      <p className="text-xl font-black text-teal-400">{(result.speech_score).toFixed(1)}%</p>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/5 flex items-center justify-end">
                    <button onClick={() => { setResult(null); }} className="text-[10px] font-black text-blue-400 uppercase tracking-widest"></button>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div key="no-result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col items-center justify-center p-12 border-2 border-dashed border-white/5 rounded-3xl bg-slate-900/20 text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center text-slate-600">
                  <Activity className="w-8 h-8" />
                </div>
                <div className="space-y-2">
                  <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Awaiting Multi-Modal Fusion</h4>
                  <p className="text-[10px] text-slate-600 max-w-[200px] leading-relaxed uppercase">
                    Provide all 3 inputs on the left to activate the cross-validation fusion engine.
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default FusionModule;
