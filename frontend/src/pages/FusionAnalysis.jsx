import React from 'react';
import FusionModule from '../components/FusionModule';
import { motion } from 'framer-motion';

const FusionAnalysis = () => {
  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-black font-outfit">Multi-Modal Fusion</h1>
        <p className="text-slate-400">Integrated diagnostic engine combining facial and vocal risk factors.</p>
      </div>
      <FusionModule />
    </motion.div>
  );
};

export default FusionAnalysis;
