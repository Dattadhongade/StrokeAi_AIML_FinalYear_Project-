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
import Login from './pages/Login';
import Register from './pages/Register';

// Auth Components
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { GoogleOAuthProvider } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your-google-client-id-here';

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
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
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Protected Routes */}
                <Route path="/face" element={<ProtectedRoute><FaceAnalysis /></ProtectedRoute>} />
                <Route path="/speech" element={<ProtectedRoute><SpeechAnalysis /></ProtectedRoute>} />
                <Route path="/fusion" element={<ProtectedRoute><FusionAnalysis /></ProtectedRoute>} />
              </Routes>
            </main>

            <Footer />
            <Chatbot />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
