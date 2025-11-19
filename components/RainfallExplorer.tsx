import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { DroughtRiskData } from '../types';

interface RainfallExplorerProps {
  initialRisk?: number;
  regionName?: string;
}

const RainfallExplorer: React.FC<RainfallExplorerProps> = ({ initialRisk = 42, regionName = "Taranaki" }) => {
  const [weeklyRainfall, setWeeklyRainfall] = useState<number>(10); // Default 10mm/week
  const [projectionData, setProjectionData] = useState<any[]>([]);

  // Constants for the simulation
  const DAYS_TO_PROJECT = 30;
  const DAILY_EVAPORATION = 3.5; // mm/day (Typical summer demand)
  const CRITICAL_THRESHOLD = 80; // Risk score where it becomes critical
  const RECOVERY_THRESHOLD = 20; // Risk score where it is considered recovered

  useEffect(() => {
    calculateProjection();
  }, [weeklyRainfall, initialRisk]);

  const calculateProjection = () => {
    const data = [];
    let currentRisk = initialRisk;
    const dailyRainfall = weeklyRainfall / 7;
    
    // Sensitivity: How much risk score changes per mm of deficit/surplus
    // Arbitrary scaling factor to make the game playable/realistic
    // If deficit is 3.5mm/day (0 rain), risk should rise significantly over 30 days.
    // Say +1.5 risk points per mm of deficit.
    const RISK_SENSITIVITY = 1.5;

    for (let day = 0; day <= DAYS_TO_PROJECT; day++) {
      data.push({
        day: `Day ${day}`,
        risk: Math.round(currentRisk * 10) / 10,
        threshold: CRITICAL_THRESHOLD
      });

      const dailyDeficit = DAILY_EVAPORATION - dailyRainfall;
      
      // Update risk
      // If deficit > 0 (drying), risk goes up.
      // If deficit < 0 (wetting), risk goes down.
      currentRisk += dailyDeficit * RISK_SENSITIVITY;

      // Clamp risk between 0 and 100
      currentRisk = Math.max(0, Math.min(100, currentRisk));
    }

    setProjectionData(data);
  };

  const getRiskColor = (risk: number) => {
    if (risk >= 80) return '#ef4444'; // Red
    if (risk >= 50) return '#f97316'; // Orange
    if (risk >= 20) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  const finalRisk = projectionData.length > 0 ? projectionData[projectionData.length - 1].risk : initialRisk;
  const isCritical = finalRisk >= CRITICAL_THRESHOLD;
  const isSafe = finalRisk <= RECOVERY_THRESHOLD;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span className="text-2xl">🌧️</span> Rainfall Scenario Explorer
        </h2>
        <p className="text-slate-500 text-sm mt-1">
          Project drought risk for <strong>{regionName}</strong> over the next 30 days based on rainfall scenarios.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-50 p-5 rounded-lg border border-slate-100">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Weekly Rainfall Scenario
            </label>
            <div className="flex items-center gap-4 mb-2">
              <input
                type="range"
                min="0"
                max="50"
                step="1"
                value={weeklyRainfall}
                onChange={(e) => setWeeklyRainfall(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <span className="text-lg font-bold text-blue-600 w-16 text-right">
                {weeklyRainfall}mm
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Adjust to simulate dry spells (0-10mm) or recovery rains (30mm+).
            </p>
          </div>

          <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
            <h3 className="font-semibold text-blue-900 mb-2">Analysis</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-blue-700">Daily Demand (Evap):</span>
                <span className="font-medium text-blue-900">{DAILY_EVAPORATION} mm/day</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Scenario Supply:</span>
                <span className="font-medium text-blue-900">{(weeklyRainfall / 7).toFixed(1)} mm/day</span>
              </div>
              <div className="pt-2 border-t border-blue-200 flex justify-between font-bold">
                <span className="text-blue-800">Net Balance:</span>
                <span className={`${(weeklyRainfall / 7) - DAILY_EVAPORATION >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {((weeklyRainfall / 7) - DAILY_EVAPORATION).toFixed(1)} mm/day
                </span>
              </div>
            </div>
          </div>

          <div className={`p-4 rounded-lg border ${isCritical ? 'bg-red-50 border-red-100' : isSafe ? 'bg-green-50 border-green-100' : 'bg-orange-50 border-orange-100'}`}>
            <h4 className={`font-bold ${isCritical ? 'text-red-800' : isSafe ? 'text-green-800' : 'text-orange-800'}`}>
              {isCritical ? 'CRITICAL RISK' : isSafe ? 'RECOVERY LIKELY' : 'CAUTION NEEDED'}
            </h4>
            <p className={`text-sm mt-1 ${isCritical ? 'text-red-700' : isSafe ? 'text-green-700' : 'text-orange-700'}`}>
              {isCritical 
                ? `At ${weeklyRainfall}mm/week, risk hits critical levels.` 
                : isSafe 
                  ? `At ${weeklyRainfall}mm/week, the region recovers.` 
                  : `Risk remains elevated. Need >${Math.ceil(DAILY_EVAPORATION * 7)}mm/week to improve.`}
            </p>
          </div>
        </div>

        {/* Chart */}
        <div className="lg:col-span-2 h-[350px] bg-white rounded-lg border border-slate-100 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={projectionData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="day" 
                tick={{ fontSize: 12 }} 
                interval={6}
                stroke="#94a3b8"
              />
              <YAxis 
                domain={[0, 100]} 
                label={{ value: 'Drought Risk Score', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b' } }}
                tick={{ fontSize: 12 }}
                stroke="#94a3b8"
              />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <ReferenceLine y={CRITICAL_THRESHOLD} label="Critical" stroke="red" strokeDasharray="3 3" />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="risk" 
                name="Projected Risk" 
                stroke="#2563eb" 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default RainfallExplorer;
