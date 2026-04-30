import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, X, Bot, User, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! I am your StrokeAI assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      // Get current analysis context from localStorage
      const analysisData = localStorage.getItem('stroke_analysis_result');
      const context = analysisData ? JSON.parse(analysisData) : null;

      const response = await axios.post(`${API_BASE}/chat`, {
        message: userMsg,
        context: context
      });

      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: response.data.response,
        emergency: response.data.emergency 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: "Sorry, I'm having trouble connecting to the server. Please check your connection." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-outfit">
      {/* Chat Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full bg-linear-to-tr from-blue-600 to-indigo-600 shadow-2xl shadow-blue-500/40 flex items-center justify-center text-white relative group"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }}>
              <X className="w-6 h-6" />
            </motion.div>
          ) : (
            <motion.div key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }}>
              <MessageSquare className="w-6 h-6" />
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Pulsing indicator if high risk detected (could be added) */}
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9, transformOrigin: 'bottom right' }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="absolute bottom-20 right-0 w-[350px] sm:w-[400px] h-[500px] bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-3xl shadow-3xl overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-4 bg-linear-to-r from-blue-600/20 to-indigo-600/20 border-b border-white/5 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">StrokeAI Assistant</h3>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Online & Ready</span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: msg.role === 'bot' ? -10 : 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex ${msg.role === 'bot' ? 'justify-start' : 'justify-end'}`}
                >
                  <div className={`max-w-[85%] flex gap-3 ${msg.role === 'bot' ? 'flex-row' : 'flex-row-reverse'}`}>
                    <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center ${
                      msg.role === 'bot' ? 'bg-slate-800 text-blue-400' : 'bg-blue-600 text-white'
                    }`}>
                      {msg.role === 'bot' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                    </div>
                    <div className={`p-3 rounded-2xl text-sm leading-relaxed ${
                      msg.role === 'bot' 
                        ? (msg.emergency ? 'bg-red-500/10 border border-red-500/20 text-red-200' : 'bg-slate-800/50 border border-white/5 text-slate-200')
                        : 'bg-blue-600 text-white font-medium'
                    }`}>
                      {msg.emergency && <div className="flex items-center gap-2 mb-2 text-red-500 font-bold uppercase text-[10px] tracking-widest">
                        <AlertCircle className="w-3 h-3" /> Emergency Alert
                      </div>}
                      {msg.content.split('\n').map((line, i) => (
                        <p key={i}>{line}</p>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800/50 p-3 rounded-2xl flex gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-100" />
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce delay-200" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-4 border-t border-white/5 bg-slate-900/50">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about stroke, results, or FAST..."
                  className="w-full bg-slate-800 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white placeholder:text-slate-500 focus:outline-hidden focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || loading}
                  className="absolute right-2 top-1.5 w-9 h-9 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:bg-slate-700 text-white flex items-center justify-center transition-colors shadow-lg"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
};

export default Chatbot;
