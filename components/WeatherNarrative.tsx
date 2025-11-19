import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../constants';

interface NarrativeData {
  narrative: string;
  generated_at: string;
  sentences?: string[];
}

const WeatherNarrative: React.FC = () => {
  const [data, setData] = useState<NarrativeData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadNarrative = async () => {
      try {
        console.log('WeatherNarrative: Fetching narrative...');
        const response = await fetch(`${API_BASE_URL}/api/public/weather-narrative`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const narrativeData = await response.json();
        console.log('WeatherNarrative: Data loaded:', narrativeData);

        // Split narrative into sentences for scrolling
        const sentences = narrativeData.narrative
          .split(/(?<=[.!?])\s+/)
          .filter((s: string) => s.trim().length > 0);

        setData({ ...narrativeData, sentences });
        setError(null);
        setIsLoading(false);
      } catch (error) {
        console.error('WeatherNarrative: Failed to load:', error);
        setError(error instanceof Error ? error.message : 'Unknown error');
        setIsLoading(false);
      }
    };

    loadNarrative();

    // Refresh every 30 minutes
    const interval = setInterval(loadNarrative, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    console.error('WeatherNarrative: Error state:', error);
    return null;
  }

  if (isLoading) {
    console.log('WeatherNarrative: Loading...');
    return null;
  }

  if (!data) {
    console.log('WeatherNarrative: No data');
    return null;
  }

  console.log('WeatherNarrative: Rendering with data:', data.narrative.substring(0, 50));

  const sentences = data.sentences || [data.narrative];

  return (
    <div className="w-full bg-gradient-to-r from-indigo-950 via-violet-900 to-indigo-950 text-white overflow-hidden py-4 px-6 flex items-center gap-4 border-t border-b border-indigo-800 shadow-xl">
      <div className="flex items-center gap-2.5 text-violet-300 whitespace-nowrap">
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
        </svg>
        <span className="text-xs font-semibold uppercase tracking-widest opacity-90">Land & Water Story</span>
      </div>

      <div className="flex-1 overflow-hidden relative h-8">
        <div className="animate-narrative-scroll whitespace-nowrap absolute flex gap-8 items-center">
          {sentences.concat(sentences).map((sentence, idx) => (
            <span key={idx} className="text-sm leading-relaxed text-slate-100 italic font-light tracking-wide flex items-center gap-8">
              {sentence}
              <span className="text-violet-500">•</span>
            </span>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs text-violet-400 whitespace-nowrap opacity-70">
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="hidden md:inline">Refreshes every 30 min</span>
      </div>

      <style>{`
        .animate-narrative-scroll {
          animation: narrative-scroll 480s linear infinite;
        }
        @keyframes narrative-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-narrative-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default WeatherNarrative;
