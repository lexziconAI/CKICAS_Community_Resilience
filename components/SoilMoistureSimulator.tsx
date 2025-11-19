import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';

const SoilMoistureSimulator: React.FC = () => {
  const [temperature, setTemperature] = useState(20);
  const [humidity, setHumidity] = useState(60);
  const [data, setData] = useState<any[]>([]);
  const [criticalDay, setCriticalDay] = useState<number | null>(null);

  useEffect(() => {
    calculateSimulation();
  }, [temperature, humidity]);

  const calculateSimulation = () => {
    const initial_moisture = 70;
    let current_moisture = initial_moisture;
    const results = [];
    let critical_day_found = null;

    for (let day = 0; day <= 30; day++) {
      // Simplified ET calculation
      const humidity_deficit = Math.max(0, 80 - humidity) / 100;
      const temp_factor = Math.max(0, temperature - 10) / 30;
      const et_rate_mm = 2 + (temp_factor * 4) + (humidity_deficit * 3);
      const moisture_loss_pct = (et_rate_mm / 150) * 100;

      let status = 'optimal';
      if (current_moisture <= 20) {
        status = 'critical';
        if (critical_day_found === null) {
          critical_day_found = day;
        }
      } else if (current_moisture <= 40) {
        status = 'stress';
      } else if (current_moisture <= 60) {
        status = 'adequate';
      }

      results.push({
        day,
        moisture: Math.max(0, Math.round(current_moisture * 10) / 10),
        status
      });

      current_moisture -= moisture_loss_pct;
    }

    setData(results);
    setCriticalDay(critical_day_found);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'optimal': return '#10b981'; // green
      case 'adequate': return '#3b82f6'; // blue
      case 'stress': return '#f59e0b'; // orange
      case 'critical': return '#ef4444'; // red
      default: return '#gray';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">🌱 Soil Moisture Decay Simulator</h3>
        <p className="text-sm text-gray-600">
          Explore how temperature and humidity affect soil moisture over time. Based on simplified Penman-Monteith evapotranspiration model.
        </p>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Temperature: {temperature}°C
          </label>
          <input
            type="range"
            min="10"
            max="35"
            value={temperature}
            onChange={(e) => setTemperature(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10°C</span>
            <span>35°C</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Humidity: {humidity}%
          </label>
          <input
            type="range"
            min="20"
            max="90"
            value={humidity}
            onChange={(e) => setHumidity(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>20%</span>
            <span>90%</span>
          </div>
        </div>
      </div>

      {/* Alert */}
      {criticalDay !== null && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                <strong>Critical threshold reached in {criticalDay} days</strong> - Soil moisture drops below 20% (crop stress level)
              </p>
            </div>
          </div>
        </div>
      )}

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
              label={{ value: 'Soil Moisture (%)', angle: -90, position: 'insideLeft' }}
              domain={[0, 100]}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded shadow">
                      <p className="text-sm font-semibold">Day {data.day}</p>
                      <p className="text-sm">Moisture: {data.moisture}%</p>
                      <p className="text-sm capitalize" style={{ color: getStatusColor(data.status) }}>
                        Status: {data.status}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <ReferenceLine y={60} stroke="#10b981" strokeDasharray="3 3" label="Optimal" />
            <ReferenceLine y={40} stroke="#f59e0b" strokeDasharray="3 3" label="Stress" />
            <ReferenceLine y={20} stroke="#ef4444" strokeDasharray="3 3" label="Critical" />
            <Line
              type="monotone"
              dataKey="moisture"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Soil Moisture %"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span>Optimal (&gt;60%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>Adequate (40-60%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500"></div>
          <span>Stress (20-40%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span>Critical (&lt;20%)</span>
        </div>
      </div>

      {/* Educational Note */}
      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>💡 Systems Thinking:</strong> This model shows the <em>feedback loop</em> between weather conditions and soil moisture.
          High temperature + low humidity = faster moisture loss. Notice how the system can cross critical thresholds
          even with gradual changes. This is a <em>threshold effect</em> - behavior changes dramatically at 20% moisture.
        </p>
      </div>
    </div>
  );
};

export default SoilMoistureSimulator;
