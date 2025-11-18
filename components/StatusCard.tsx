import React from 'react';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  status?: 'success' | 'warning' | 'error' | 'neutral';
  icon?: React.ReactNode;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, value, subtitle, status = 'neutral', icon }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-white text-slate-800 border-slate-200';
    }
  };

  return (
    <div className={`p-4 rounded-lg border shadow-sm ${getStatusColor()} transition-all duration-200`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider opacity-70 mb-1">{title}</h3>
          <div className="text-2xl font-bold">{value}</div>
          {subtitle && <div className="text-sm opacity-80 mt-1">{subtitle}</div>}
        </div>
        {icon && <div className="opacity-50">{icon}</div>}
      </div>
    </div>
  );
};

export default StatusCard;