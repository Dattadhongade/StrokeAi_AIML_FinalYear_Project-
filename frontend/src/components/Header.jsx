import React, { useState } from 'react';
import { Activity, User, LogOut, Menu, X } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  const navItems = [
    { name: 'Home', path: '/', isExternal: false },
    { name: 'Face Analysis', path: '/face', isExternal: false },
    { name: 'Speech Analysis', path: '/speech', isExternal: false },
    { name: 'Fusion Model', path: '/fusion', isExternal: false },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md border-b border-white/5 bg-slate-950/50">
      <div className="container mx-auto px-4 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Activity className="text-white w-6 h-6" />
          </div>
          <span className="text-2xl font-bold font-outfit tracking-tight">
            Stroke<span className="text-blue-500">AI</span>
          </span>
        </Link>
        
        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            item.isExternal ? (
              <a 
                key={item.path}
                href={item.path}
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm font-semibold text-slate-400 hover:text-orange-400 transition-colors"
              >
                {item.name} ↗
              </a>
            ) : (
              <Link 
                key={item.path}
                to={item.path}
                className={`text-sm font-semibold transition-colors ${
                  location.pathname === item.path ? 'text-blue-400' : 'text-slate-400 hover:text-white'
                }`}
              >
                {item.name}
              </Link>
            )
          ))}
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg bg-slate-800 text-sm font-bold hover:bg-slate-700 transition-colors border border-white/5 hidden lg:block"
          >
            Backend Docs ↗
          </a>

          {/* Auth Section */}
          <div className="flex items-center gap-3 pl-6 border-l border-white/10">
            {user ? (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center overflow-hidden">
                    <User className="w-4 h-4 text-slate-400" />
                  </div>
                  <span className="hidden lg:block font-medium truncate max-w-[100px]">{user.name}</span>
                </div>
                <button 
                  onClick={() => {
                    logout();
                    navigate('/login');
                  }}
                  className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="px-4 py-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors">
                  Login
                </Link>
                <Link to="/register" className="px-4 py-2 text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-lg shadow-blue-500/20">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Clinical Mode Toggle */}
          <div className="flex items-center gap-3 pl-6 border-l border-white/10">
            <span className={`text-[10px] font-black uppercase tracking-widest ${!JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'text-blue-400' : 'text-slate-600'}`}>Demo</span>
            <button 
              onClick={() => {
                const current = JSON.parse(localStorage.getItem('clinical_mode') || 'false');
                localStorage.setItem('clinical_mode', JSON.stringify(!current));
                window.location.reload(); // Refresh to apply clinical context
              }}
              className="relative w-10 h-5 rounded-full bg-slate-800 border border-white/10 transition-colors"
            >
              <div className={`absolute top-0.5 left-0.5 w-3.5 h-3.5 rounded-full bg-white transition-transform ${JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'translate-x-5 bg-blue-500' : 'translate-x-0'}`} />
            </button>
            <span className={`text-[10px] font-black uppercase tracking-widest ${JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'text-blue-400' : 'text-slate-600'}`}>Clinical</span>
          </div>
        </nav>
        <button 
          className="md:hidden p-2 text-slate-300 hover:text-white transition-colors"
          onClick={toggleMobileMenu}
        >
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-20 left-0 w-full bg-slate-950/95 backdrop-blur-xl border-b border-white/5 py-6 px-4 flex flex-col gap-6 shadow-2xl">
          <nav className="flex flex-col gap-4">
            {navItems.map((item) => (
              item.isExternal ? (
                <a 
                  key={item.path}
                  href={item.path}
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-lg font-semibold text-slate-400 hover:text-orange-400 transition-colors"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name} ↗
                </a>
              ) : (
                <Link 
                  key={item.path}
                  to={item.path}
                  className={`text-lg font-semibold transition-colors ${
                    location.pathname === item.path ? 'text-blue-400' : 'text-slate-400 hover:text-white'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              )
            ))}
          </nav>
          
          <div className="h-px w-full bg-slate-800"></div>

          {/* Auth Section Mobile */}
          <div className="flex flex-col gap-4">
            {user ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                    <User className="w-5 h-5 text-slate-400" />
                  </div>
                  <span className="font-medium text-white">{user.name}</span>
                </div>
                <button 
                  onClick={() => {
                    logout();
                    navigate('/login');
                    setIsMobileMenuOpen(false);
                  }}
                  className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-semibold">Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <Link 
                  to="/login" 
                  className="w-full py-3 text-center font-semibold text-slate-300 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  className="w-full py-3 text-center font-bold bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          <div className="h-px w-full bg-slate-800"></div>

          {/* Clinical Mode Mobile */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-slate-400">Mode</span>
            <div className="flex items-center gap-3">
              <span className={`text-[10px] font-black uppercase tracking-widest ${!JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'text-blue-400' : 'text-slate-600'}`}>Demo</span>
              <button 
                onClick={() => {
                  const current = JSON.parse(localStorage.getItem('clinical_mode') || 'false');
                  localStorage.setItem('clinical_mode', JSON.stringify(!current));
                  window.location.reload();
                }}
                className="relative w-12 h-6 rounded-full bg-slate-800 border border-white/10 transition-colors"
              >
                <div className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'translate-x-6 bg-blue-500' : 'translate-x-0'}`} />
              </button>
              <span className={`text-[10px] font-black uppercase tracking-widest ${JSON.parse(localStorage.getItem('clinical_mode') || 'false') ? 'text-blue-400' : 'text-slate-600'}`}>Clinical</span>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
