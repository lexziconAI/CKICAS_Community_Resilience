import React from 'react';

const TriggersSkeleton: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Skeleton Card 1 */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="h-5 bg-slate-200 rounded w-48 mb-2"></div>
            <div className="h-4 bg-slate-100 rounded w-32"></div>
          </div>
          <div className="h-6 w-16 bg-slate-200 rounded-full"></div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="h-4 bg-slate-100 rounded"></div>
          <div className="h-4 bg-slate-100 rounded"></div>
        </div>
        <div className="flex gap-2">
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
        </div>
      </div>

      {/* Skeleton Card 2 */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="h-5 bg-slate-200 rounded w-48 mb-2"></div>
            <div className="h-4 bg-slate-100 rounded w-32"></div>
          </div>
          <div className="h-6 w-16 bg-slate-200 rounded-full"></div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="h-4 bg-slate-100 rounded"></div>
          <div className="h-4 bg-slate-100 rounded"></div>
        </div>
        <div className="flex gap-2">
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
        </div>
      </div>

      {/* Skeleton Card 3 */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="h-5 bg-slate-200 rounded w-48 mb-2"></div>
            <div className="h-4 bg-slate-100 rounded w-32"></div>
          </div>
          <div className="h-6 w-16 bg-slate-200 rounded-full"></div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="h-4 bg-slate-100 rounded"></div>
          <div className="h-4 bg-slate-100 rounded"></div>
        </div>
        <div className="flex gap-2">
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
          <div className="h-8 w-20 bg-slate-200 rounded"></div>
        </div>
      </div>
    </div>
  );
};

export default TriggersSkeleton;
