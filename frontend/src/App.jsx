import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Chatbot from './components/Chatbot';

// Pages
import Home from './pages/Home';
import FaceAnalysis from './pages/FaceAnalysis';
import SpeechAnalysis from './pages/SpeechAnalysis';
import FusionAnalysis from './pages/FusionAnalysis';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col">
        {/* Background Glows */}
        <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full"></div>
          <div className="absolute bottom-[10%] right-[-5%] w-[35%] h-[35%] bg-teal-500/10 blur-[100px] rounded-full"></div>
        </div>

        <Header />
        
        <main className="flex-1 container mx-auto px-4 py-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/face" element={<FaceAnalysis />} />
            <Route path="/speech" element={<SpeechAnalysis />} />
            <Route path="/fusion" element={<FusionAnalysis />} />
          </Routes>
        </main>

        <Footer />
        <Chatbot />
      </div>
    </BrowserRouter>
  );
}

export default App;
