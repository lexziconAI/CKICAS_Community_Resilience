import React from 'react';

const WeatherMetricsSkeleton: React.FC = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 animate-pulse">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between mb-4">
        <div className="h-6 bg-slate-300 rounded w-48"></div>
        <div className="h-5 bg-slate-200 rounded w-16"></div>
      </div>

      {/* Metrics Grid Skeleton */}
      <div className="grid grid-cols-2 gap-4">
        {/* Metric 1 */}
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="h-3 bg-slate-200 rounded w-20 mb-2"></div>
          <div className="h-7 bg-slate-300 rounded w-24"></div>
        </div>

        {/* Metric 2 */}
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="h-3 bg-slate-200 rounded w-16 mb-2"></div>
          <div className="h-7 bg-slate-300 rounded w-20"></div>
        </div>

        {/* Metric 3 */}
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="h-3 bg-slate-200 rounded w-18 mb-2"></div>
          <div className="h-7 bg-slate-300 rounded w-24"></div>
        </div>

        {/* Metric 4 */}
        <div className="p-3 bg-slate-50 rounded-lg">
          <div className="h-3 bg-slate-200 rounded w-20 mb-2"></div>
          <div className="h-7 bg-slate-300 rounded w-20"></div>
        </div>
      </div>
    </div>
  );
};

export default WeatherMetricsSkeleton;
