import React, { useEffect, useState } from 'react';
import { fetchNewsHeadlines } from '../services/api';

interface NewsHeadline {
  title: string;
  source: string;
  link: string;
  published: string;
}

const NewsTicker: React.FC = () => {
  const [headlines, setHeadlines] = useState<NewsHeadline[]>([]);

  useEffect(() => {
    const loadHeadlines = async () => {
      const data = await fetchNewsHeadlines();
      // Filter out news older than 2 weeks
      const twoWeeksAgo = new Date();
      twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);

      const recentHeadlines = data.filter(headline => {
        const publishedDate = new Date(headline.published);
        return publishedDate >= twoWeeksAgo;
      });

      setHeadlines(recentHeadlines);
    };
    loadHeadlines();
  }, []);

  if (headlines.length === 0) return null;

  return (
    <div className="w-full bg-gradient-to-r from-emerald-900 via-teal-900 to-emerald-900 text-white overflow-hidden py-3 px-4 flex items-center gap-4 border-t border-b border-emerald-700 shadow-lg">
      <div className="flex items-center gap-2.5 text-emerald-300 whitespace-nowrap">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
        </svg>
        <span className="text-xs font-bold uppercase tracking-wider">Rural News</span>
      </div>

      <div className="flex-1 overflow-hidden relative h-7">
        <div className="animate-news-scroll whitespace-nowrap absolute flex gap-8 items-center">
          {headlines.concat(headlines).map((headline, idx) => (
            <a
              key={idx}
              href={headline.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-slate-200 hover:text-white hover:underline transition-colors flex items-center gap-2.5 group"
            >
              <span className="text-emerald-400 text-xs font-medium">[{headline.source}]</span>
              <span className="group-hover:text-white">{headline.title}</span>
              <span className="text-slate-500 text-xs">• {new Date(headline.published).toLocaleDateString('en-NZ', { month: 'short', day: 'numeric' })}</span>
            </a>
          ))}
        </div>
      </div>

      <div className="text-xs text-slate-500 whitespace-nowrap hidden md:block">
        {headlines.length} {headlines.length === 1 ? 'headline' : 'headlines'}
      </div>

      <style>{`
        .animate-news-scroll {
          animation: news-scroll 60s linear infinite;
        }
        @keyframes news-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-news-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default NewsTicker;
