import React from 'react';
import {
  AlertTriangle, Code, User,
  Mail, Globe, Shield, Activity
} from 'lucide-react';

const Footer = () => {
  return (
    <footer className="mt-24 border-t border-white/5 bg-black/40 backdrop-blur-xl">
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand Column */}
          <div className="col-span-1 md:col-span-1 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Activity className="text-white w-5 h-5" />
              </div>
              <span className="text-xl font-black font-outfit tracking-tighter text-white">StrokeAI</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed font-medium">
              Advanced multi-modal diagnostic framework for rapid stroke symptom detection using facial biometrics and acoustic analysis.
            </p>
            <div className="flex gap-4 pt-2">
              <a href="#" className="text-slate-600 hover:text-blue-400 transition-colors"><Code className="w-4 h-4" /></a>
              <a href="#" className="text-slate-600 hover:text-blue-400 transition-colors"><User className="w-4 h-4" /></a>
              <a href="#" className="text-slate-600 hover:text-blue-400 transition-colors"><Globe className="w-4 h-4" /></a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Project Modules</h4>
            <ul className="space-y-2 text-xs font-bold text-slate-500">
              <li><a href="#" className="hover:text-blue-400 transition-all">Facial Asymmetry Engine</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-all">Acoustic Dysarthria Model</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-all">Clinical Metadata Fusion</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-all">XAI Reasoning Engine</a></li>
            </ul>
          </div>

          {/* Tech Stack */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Neuro-Technology</h4>
            <ul className="space-y-2 text-xs font-bold text-slate-500">
              <li>FastAPI / Python Backend</li>
              <li>React / Tailwind Frontend</li>
              <li>OpenCV & Mediapipe</li>
              <li>Scikit-Learn Models</li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Development</h4>
            <div className="flex items-center gap-3 text-xs font-bold text-slate-500">
              <Mail className="w-4 h-4 text-blue-500/50" />
              <span>research@strokeai.io</span>
            </div>
            <div className="flex items-center gap-3 text-xs font-bold text-slate-500">
              <Shield className="w-4 h-4 text-green-500/50" />
              <span></span>
            </div>
          </div>
        </div>

        {/* Medical Disclaimer */}
        <div className="p-6 rounded-2xl bg-amber-500/5 border border-amber-500/10 flex gap-4 mb-12">
          <AlertTriangle className="w-6 h-6 text-amber-500 shrink-0" />
          <div className="text-[11px] leading-relaxed text-amber-200/60 font-medium">
            <strong className="text-amber-500 font-black uppercase tracking-widest mr-2">Medical Disclaimer:</strong>
            This system is a research demonstration project and is NOT a certified medical device.
            The analysis provided is for informational purposes only and should never be used as a substitute for professional
            medical diagnosis, advice, or treatment. If you suspect a stroke, CALL EMERGENCY SERVICES IMMEDIATELY.
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/5 gap-4 text-[10px] font-black uppercase tracking-widest text-slate-600">
          <p>© 2026 STROKE-AI FRAMEWORK</p>
          <div className="flex gap-8">
            <a href="#" className="hover:text-white transition-colors">Privacy Protocol</a>
            <a href="#" className="hover:text-white transition-colors">Academic Terms</a>
            <a href="#" className="hover:text-white transition-colors">Contact Devs</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
