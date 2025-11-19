import React from 'react';

const HistoricalChartSkeleton: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-full flex flex-col animate-pulse" style={{ minHeight: '180px', maxHeight: '220px' }}>
      {/* Header Skeleton */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="h-5 bg-slate-300 rounded w-32 mb-2"></div>
          <div className="h-4 bg-slate-200 rounded w-24"></div>
        </div>
        <div className="h-4 bg-slate-200 rounded w-20"></div>
      </div>

      {/* Chart Area Skeleton */}
      <div className="flex-1 flex items-end justify-between gap-2 px-4">
        {/* Simulated chart bars with varying heights */}
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '60%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '75%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '45%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '90%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '55%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '70%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
        <div className="flex flex-col items-center flex-1">
          <div className="w-full bg-slate-200 rounded-t" style={{ height: '50%' }}></div>
          <div className="h-3 bg-slate-200 rounded w-8 mt-2"></div>
        </div>
      </div>

      {/* Legend Skeleton */}
      <div className="flex items-center gap-4 mt-4 justify-center">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-slate-200 rounded"></div>
          <div className="h-3 bg-slate-200 rounded w-16"></div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-slate-200 rounded"></div>
          <div className="h-3 bg-slate-200 rounded w-20"></div>
        </div>
      </div>
    </div>
  );
};

export default HistoricalChartSkeleton;
