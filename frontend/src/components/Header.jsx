import React from 'react';
import { Activity } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

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
            className="px-4 py-2 rounded-lg bg-slate-800 text-sm font-bold hover:bg-slate-700 transition-colors border border-white/5"
          >
            Backend Docs ↗
          </a>

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
      </div>
    </header>
  );
};

export default Header;
