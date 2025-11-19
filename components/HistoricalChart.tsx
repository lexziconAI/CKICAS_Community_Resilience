import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { HistoricalDataPoint } from '../types';

interface HistoricalChartProps {
  data: HistoricalDataPoint[];
  regionName: string;
}

const HistoricalChart: React.FC<HistoricalChartProps> = ({ data, regionName }) => {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 h-full flex flex-col overflow-hidden">
      <div className="mb-3">
        <h3 className="font-bold text-lg text-slate-800">7-Day Forecast Trend</h3>
        <p className="text-xs text-slate-500">Projected Soil Moisture & Rain Probability for {regionName}</p>
      </div>

      <div className="flex-1 pb-2" style={{ minHeight: '180px', maxHeight: '220px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{
              top: 5,
              right: 10,
              left: -10,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fontSize: 11, fill: '#64748b'}} dy={5} />
            <YAxis axisLine={false} tickLine={false} tick={{fontSize: 11, fill: '#64748b'}} />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend iconType="circle" wrapperStyle={{fontSize: '11px', paddingTop: '4px'}} />
            <Area
              type="monotone"
              dataKey="soil_moisture"
              name="Soil Moisture Index"
              stackId="1"
              stroke="#3b82f6"
              fill="#93c5fd"
            />
            <Area
              type="monotone"
              dataKey="risk_score"
              name="Drought Risk"
              stackId="2"
              stroke="#ef4444"
              fill="#fca5a5"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default HistoricalChart;
