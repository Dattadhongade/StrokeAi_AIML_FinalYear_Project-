import React from 'react';
import AnalysisModule from '../components/AnalysisModule';
import { motion } from 'framer-motion';

const FaceAnalysis = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-black font-outfit">Facial Biometrics</h1>
        <p className="text-slate-400">Deep learning analysis of facial symmetry and landmark deviations.</p>
      </div>
      <AnalysisModule 
        type="face"
        title="Geometric Asymmetry Analysis"
        description="Our CNN model identifies facial keypoints to detect subtle drooping often invisible to the naked eye. Capture a live photo or upload an existing image."
      />
    </motion.div>
  );
};

export default FaceAnalysis;
