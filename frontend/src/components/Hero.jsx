import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Zap, BarChart3 } from 'lucide-react';

const Hero = () => {
  return (
    <section className="relative pt-10 pb-20 overflow-hidden">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-semibold tracking-wide"
        >
          <Zap className="w-4 h-4 fill-blue-400" />
          Multi-Modal Deep Learning
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl md:text-7xl font-extrabold font-outfit leading-[1.1] tracking-tight"
        >
          Early Stroke Risk<br />
          <span className="gradient-text">Detection System</span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed"
        >
          Combines <strong className="text-slate-200">facial asymmetry analysis</strong> and <strong className="text-slate-200">speech abnormality detection</strong> in a weighted fusion model for real-time stroke risk assessment.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-wrap justify-center gap-4 pt-4"
        >
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-white/5 backdrop-blur-sm">
            <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
            <span className="text-sm font-medium">Face: 60% Weight</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-white/5 backdrop-blur-sm">
            <div className="w-2 h-2 rounded-full bg-teal-500 shadow-[0_0_8px_rgba(20,184,166,0.5)]"></div>
            <span className="text-sm font-medium">Speech: 40% Weight</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-white/5 backdrop-blur-sm">
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium">FAST Criteria</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="pt-8"
        >
          <a href="#face-section" className="btn-primary inline-flex items-center gap-2 group">
            Begin Assessment
            <BarChart3 className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </a>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
