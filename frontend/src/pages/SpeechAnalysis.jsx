import React from 'react';
import AnalysisModule from '../components/AnalysisModule';
import { motion } from 'framer-motion';

const SpeechAnalysis = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-black font-outfit">Neural Speech Processing</h1>
        <p className="text-slate-400">MFCC-based analysis of prosody and spectral centroid shifts for dysarthria detection.</p>
      </div>
      <AnalysisModule 
        type="speech"
        title="Speech Impairment Detection"
        description="Our LSTM neural network processes Mel-frequency cepstral coefficients to identify slurred speech or abnormal pauses."
      />
    </motion.div>
  );
};

export default SpeechAnalysis;
