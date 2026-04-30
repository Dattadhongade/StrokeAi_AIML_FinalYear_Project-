import React from 'react';
import Hero from '../components/Hero';
import { motion } from 'framer-motion';
import { Activity, Brain, Shield, ClipboardList, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  Filler
);

const Home = () => {
  const features = [
    {
      icon: <Activity className="text-blue-500 w-8 h-8" />,
      title: "Face Analysis",
      desc: "Advanced geometric landmark detection to identify subtle facial drooping or asymmetry.",
      link: "/face",
      isExternal: false
    },
    {
      icon: <Brain className="text-purple-500 w-8 h-8" />,
      title: "Speech Analysis",
      desc: "LSTM-based neural networks trained to detect slurring and prosodic flattening in real-time.",
      link: "/speech",
      isExternal: false
    },
    {
      icon: <Shield className="text-teal-500 w-8 h-8" />,
      title: "Fusion Model",
      desc: "Multi-modal weighted analysis providing a clinically-calibrated stroke risk coefficient.",
      link: "/fusion",
      isExternal: false
    }
  ];

  return (
    <div className="space-y-24">
      <Hero />
      
      {/* Features Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 py-12">
        {features.map((feature, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-8 group hover:border-blue-500/30 transition-all cursor-default flex flex-col"
          >
            <div className="mb-6">{feature.icon}</div>
            <h3 className="text-xl font-bold font-outfit mb-3">{feature.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed mb-6 flex-1">{feature.desc}</p>
            
            {feature.isExternal ? (
              <a 
                href={feature.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm font-bold text-orange-400 hover:text-orange-300 flex items-center gap-2 mt-auto"
              >
                Open Form ↗
              </a>
            ) : (
              <Link to={feature.link} className="text-sm font-bold text-blue-400 hover:text-blue-300 flex items-center gap-2 mt-auto">
                Explore Module →
              </Link>
            )}
          </motion.div>
        ))}
      </section>

      {/* Patient Trends Section (New) */}
      <HistoryTrends />
    </div>
  );
};

const HistoryTrends = () => {
    const [history, setHistory] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await axios.get('http://localhost:8000/history');
                setHistory(res.data);
            } catch (err) { console.error(err); }
            setLoading(false);
        };
        fetchHistory();
    }, []);

    if (loading) return <div className="text-center p-12 text-slate-500">Loading Patient Trends...</div>;
    if (history.length === 0) return null;

    const chartData = {
        labels: history.map(h => new Date(h.timestamp).toLocaleDateString()),
        datasets: [{
            label: 'Stroke Risk Score (%)',
            data: history.map(h => (h.final_score || h.face_risk_score || 0) * 100),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 6,
            pointBackgroundColor: '#3b82f6'
        }]
    };

    return (
        <section className="space-y-8 animate-in fade-in duration-700">
            <div className="flex items-center gap-4 border-l-4 border-blue-500 pl-6">
                <h2 className="text-3xl font-black font-outfit uppercase tracking-tight">Patient Diagnostic History</h2>
                <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-widest">Active Monitoring</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 glass-card p-8">
                    <div className="h-[300px]">
                        <Line 
                            data={chartData} 
                            options={{ 
                                maintainAspectRatio: false, 
                                plugins: { legend: { display: false } },
                                scales: { 
                                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                                    x: { grid: { display: false } }
                                }
                            }} 
                        />
                    </div>
                </div>

                <div className="space-y-4">
                    {history.reverse().map((entry, idx) => (
                        <div key={idx} className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-between group hover:bg-white/10 transition-colors">
                            <div className="flex flex-col">
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                                    {new Date(entry.timestamp).toLocaleDateString()}
                                </span>
                                <span className="text-sm font-bold text-slate-200">{entry.risk_label}</span>
                            </div>
                            <div className="text-right">
                                <span className={`text-xl font-black font-outfit ${
                                    entry.risk_label.includes('High') ? 'text-red-500' : 
                                    entry.risk_label.includes('Medium') ? 'text-amber-500' : 'text-green-500'
                                }`}>
                                    {((entry.final_score || entry.face_risk_score || 0) * 100).toFixed(1)}%
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Home;
