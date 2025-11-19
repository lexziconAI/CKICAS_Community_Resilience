import React from 'react';

const QuickStatsSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Skeleton Card 1 */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-3 bg-slate-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-slate-300 rounded w-12"></div>
          </div>
          <div className="bg-slate-200 p-3 rounded-lg">
            <div className="w-6 h-6 bg-slate-300 rounded"></div>
          </div>
        </div>
      </div>

      {/* Skeleton Card 2 */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-3 bg-slate-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-slate-300 rounded w-12"></div>
          </div>
          <div className="bg-slate-200 p-3 rounded-lg">
            <div className="w-6 h-6 bg-slate-300 rounded"></div>
          </div>
        </div>
      </div>

      {/* Skeleton Card 3 */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-3 bg-slate-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-slate-300 rounded w-20"></div>
          </div>
          <div className="bg-slate-200 p-3 rounded-lg">
            <div className="w-6 h-6 bg-slate-300 rounded"></div>
          </div>
        </div>
      </div>

      {/* Skeleton Card 4 */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-3 bg-slate-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-slate-300 rounded w-16"></div>
          </div>
          <div className="bg-slate-200 p-3 rounded-lg">
            <div className="w-6 h-6 bg-slate-300 rounded"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickStatsSkeleton;
