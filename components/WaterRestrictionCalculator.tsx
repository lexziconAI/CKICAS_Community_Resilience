import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';

const WaterRestrictionCalculator: React.FC = () => {
  const [restrictionLevel, setRestrictionLevel] = useState(0);
  const [currentDamLevel, setCurrentDamLevel] = useState(60);
  const [data, setData] = useState<any[]>([]);

  const restrictionLabels = [
    { level: 0, name: 'No Restrictions', color: 'green', reduction: 0 },
    { level: 1, name: 'Voluntary Conservation', color: 'blue', reduction: 10 },
    { level: 2, name: 'Sprinkler Ban', color: 'yellow', reduction: 25 },
    { level: 3, name: 'Outdoor Ban', color: 'orange', reduction: 40 },
    { level: 4, name: 'Essential Only', color: 'red', reduction: 55 }
  ];

  useEffect(() => {
    calculateProjection();
  }, [restrictionLevel, currentDamLevel]);

  const calculateProjection = () => {
    const results = [];
    let dam_level = currentDamLevel;

    // Usage rates (ML/day)
    const baseline_usage = 100;
    const reduction_factors = [1.0, 0.9, 0.75, 0.6, 0.45];
    const daily_usage = baseline_usage * reduction_factors[restrictionLevel];

    // Minimal summer inflow
    const daily_inflow = 20;
    const net_change_ML = daily_inflow - daily_usage;

    // Dam capacity
    const capacity_ML = 10000;

    for (let day = 0; day <= 90; day++) {
      let status = 'healthy';
      if (dam_level <= 30) status = 'critical';
      else if (dam_level <= 50) status = 'concern';
      else if (dam_level <= 70) status = 'watch';

      results.push({
        day,
        dam_level: Math.max(0, Math.round(dam_level * 10) / 10),
        usage: Math.round(daily_usage * 10) / 10,
        status
      });

      // Update for next day
      const current_level_ML = (dam_level / 100) * capacity_ML;
      const new_level_ML = Math.max(0, current_level_ML + net_change_ML);
      dam_level = (new_level_ML / capacity_ML) * 100;
    }

    setData(results);
  };

  const currentRestriction = restrictionLabels[restrictionLevel];
  const finalLevel = data.length > 0 ? data[data.length - 1].dam_level : currentDamLevel;
  const daysUntilCritical = data.findIndex(d => d.dam_level <= 30);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">💧 Water Restriction Impact Calculator</h3>
        <p className="text-sm text-gray-600">
          Explore how different restriction levels affect dam/reservoir levels over time. Based on real NZ water usage patterns.
        </p>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Restriction Level: {restrictionLevel} - {currentRestriction.name}
          </label>
          <input
            type="range"
            min="0"
            max="4"
            step="1"
            value={restrictionLevel}
            onChange={(e) => setRestrictionLevel(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            {restrictionLabels.map(r => (
              <span key={r.level} className="text-center">L{r.level}</span>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Current Dam Level: {currentDamLevel}%
          </label>
          <input
            type="range"
            min="20"
            max="90"
            value={currentDamLevel}
            onChange={(e) => setCurrentDamLevel(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>20%</span>
            <span>90%</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Water Usage Reduction</div>
          <div className="text-2xl font-bold text-blue-600">{currentRestriction.reduction}%</div>
          <div className="text-xs text-gray-500 mt-1">vs. unrestricted usage</div>
        </div>

        <div className="bg-cyan-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Dam Level in 90 Days</div>
          <div className="text-2xl font-bold text-cyan-600">{finalLevel}%</div>
          <div className="text-xs text-gray-500 mt-1">projected with current restrictions</div>
        </div>

        <div className={`${daysUntilCritical > 0 && daysUntilCritical < 90 ? 'bg-red-50' : 'bg-green-50'} p-4 rounded-lg`}>
          <div className="text-sm text-gray-600">Critical Level Alert</div>
          <div className={`text-2xl font-bold ${daysUntilCritical > 0 && daysUntilCritical < 90 ? 'text-red-600' : 'text-green-600'}`}>
            {daysUntilCritical > 0 && daysUntilCritical < 90 ? `Day ${daysUntilCritical}` : 'No Alert'}
          </div>
          <div className="text-xs text-gray-500 mt-1">{daysUntilCritical > 0 && daysUntilCritical < 90 ? 'when dam hits 30%' : 'stays above 30%'}</div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="day"
              label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Dam Level (%)', angle: -90, position: 'insideLeft' }}
              domain={[0, 100]}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded shadow">
                      <p className="text-sm font-semibold">Day {data.day}</p>
                      <p className="text-sm">Dam Level: {data.dam_level}%</p>
                      <p className="text-sm">Usage: {data.usage} ML/day</p>
                      <p className="text-sm capitalize text-blue-600">Status: {data.status}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <ReferenceLine y={70} stroke="#10b981" strokeDasharray="3 3" label="Healthy" />
            <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="3 3" label="Watch" />
            <ReferenceLine y={30} stroke="#ef4444" strokeDasharray="3 3" label="Critical" />
            <Line
              type="monotone"
              dataKey="dam_level"
              stroke="#06b6d4"
              strokeWidth={3}
              dot={false}
              name="Dam Level %"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Restriction Levels Guide */}
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <h4 className="font-semibold text-sm mb-3">Restriction Levels Explained:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
          <div><strong>Level 0:</strong> No restrictions - Normal usage</div>
          <div><strong>Level 1:</strong> Voluntary conservation (10% reduction)</div>
          <div><strong>Level 2:</strong> Sprinkler ban - Hand watering only (25% reduction)</div>
          <div><strong>Level 3:</strong> Outdoor ban - No outdoor use (40% reduction)</div>
          <div><strong>Level 4:</strong> Essential only - Drinking/sanitation (55% reduction)</div>
        </div>
      </div>

      {/* Educational Note */}
      <div className="bg-purple-50 p-4 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>💡 Systems Thinking:</strong> This shows a <em>policy feedback loop</em> - restrictions reduce demand,
          which extends water supply, which delays the need for further restrictions. Notice the <em>time delay</em>:
          implementing restrictions today takes weeks to show effect on dam levels. This is a classic <em>management challenge</em>
          in resource systems - act too late and you hit crisis, act too early and you face community resistance.
        </p>
      </div>
    </div>
  );
};

export default WaterRestrictionCalculator;
