import React, { useEffect, useState } from 'react';
import { fetchCouncilAlerts } from '../services/api';
import { RssFeedItem } from '../types';

const CouncilAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<RssFeedItem[]>([]);

  useEffect(() => {
    const loadAlerts = async () => {
      const data = await fetchCouncilAlerts();
      setAlerts(data);
    };
    loadAlerts();
  }, []);

  if (alerts.length === 0) return null;

  return (
    <div className="w-full bg-slate-800 text-white overflow-hidden py-2 px-4 flex items-center gap-4 border-t border-b border-slate-700">
      <div className="flex items-center gap-2 text-orange-400 whitespace-nowrap">
        <svg className="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
        </svg>
        <span className="text-xs font-bold uppercase tracking-wider">Regional Updates</span>
      </div>
      
      <div className="flex-1 overflow-hidden relative h-6">
        <div className="animate-marquee whitespace-nowrap absolute flex gap-8">
          {alerts.concat(alerts).map((alert, idx) => (
            <a 
              key={idx} 
              href={alert.link} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-sm text-slate-300 hover:text-white hover:underline transition-colors flex items-center gap-2"
            >
              <span className="text-slate-500 text-xs">[{alert.source}]</span>
              {alert.title}
            </a>
          ))}
        </div>
      </div>
      
      <style>{`
        .animate-marquee {
          animation: marquee 40s linear infinite;
        }
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default CouncilAlerts;
