import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';

const AquiferDrawdownModel: React.FC = () => {
  const [pumpingRate, setPumpingRate] = useState(500000); // L/day
  const [rechargeRate, setRechargeRate] = useState(250); // mm/year
  const [data, setData] = useState<any[]>([]);
  const [criticalYear, setCriticalYear] = useState<number | null>(null);

  useEffect(() => {
    calculateSimulation();
  }, [pumpingRate, rechargeRate]);

  const calculateSimulation = () => {
    const initial_depth = 15; // meters
    let current_depth = initial_depth;
    const aquifer_area_km2 = 50;
    const aquifer_area_m2 = aquifer_area_km2 * 1_000_000;

    // Convert pumping to mm/year
    const annual_pumping_L = pumpingRate * 365;
    const pumping_mm_per_year = (annual_pumping_L / aquifer_area_m2) * 1000;

    // Net change per year
    const net_decline_mm = pumping_mm_per_year - rechargeRate;
    const net_decline_m = net_decline_mm / 1000;

    const results = [];
    let critical_year_found = null;

    for (let year = 0; year <= 20; year++) {
      let status = 'healthy';
      if (current_depth >= 60) {
        status = 'critical';
        if (critical_year_found === null) {
          critical_year_found = year;
        }
      } else if (current_depth >= 40) {
        status = 'concern';
      } else if (current_depth >= 20) {
        status = 'watch';
      }

      results.push({
        year,
        depth: Math.round(current_depth * 10) / 10,
        status,
        net_change: Math.round(net_decline_m * 100) / 100
      });

      current_depth += net_decline_m;
    }

    setData(results);
    setCriticalYear(critical_year_found);
  };

  const finalDepth = data.length > 0 ? data[data.length - 1].depth : 15;
  const netChange = data.length > 1 ? data[1].net_change : 0;
  const isRecovering = netChange < 0;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">💧 Aquifer Drawdown Model</h3>
        <p className="text-sm text-gray-600">
          Explore long-term groundwater sustainability. Slow variables like aquifer levels take decades to change.
        </p>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pumping Rate: {(pumpingRate / 1000).toFixed(0)}k L/day
          </label>
          <input
            type="range"
            min="100000"
            max="2000000"
            step="100000"
            value={pumpingRate}
            onChange={(e) => setPumpingRate(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-red-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>100k L/day</span>
            <span>2M L/day</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Recharge Rate: {rechargeRate} mm/year
          </label>
          <input
            type="range"
            min="100"
            max="500"
            step="50"
            value={rechargeRate}
            onChange={(e) => setRechargeRate(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>100 mm/yr</span>
            <span>500 mm/yr</span>
          </div>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className={`${isRecovering ? 'bg-green-50' : 'bg-red-50'} p-4 rounded-lg`}>
          <div className="text-sm text-gray-600">Net Annual Change</div>
          <div className={`text-2xl font-bold ${isRecovering ? 'text-green-600' : 'text-red-600'}`}>
            {netChange > 0 ? '+' : ''}{netChange}m/year
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {isRecovering ? 'Aquifer recovering!' : 'Aquifer declining'}
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Depth in 20 Years</div>
          <div className="text-2xl font-bold text-blue-600">{finalDepth}m</div>
          <div className="text-xs text-gray-500 mt-1">
            from {data[0]?.depth}m today
          </div>
        </div>

        <div className={`${criticalYear !== null && criticalYear <= 20 ? 'bg-red-50' : 'bg-green-50'} p-4 rounded-lg`}>
          <div className="text-sm text-gray-600">Critical Level (60m)</div>
          <div className={`text-2xl font-bold ${criticalYear !== null && criticalYear <= 20 ? 'text-red-600' : 'text-green-600'}`}>
            {criticalYear !== null && criticalYear <= 20 ? `Year ${criticalYear}` : 'Not Reached'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {criticalYear !== null && criticalYear <= 20 ? 'pumping becomes unsustainable' : 'within 20 year horizon'}
          </div>
        </div>
      </div>

      {/* Alert */}
      {!isRecovering && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-orange-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-orange-700">
                <strong>Unsustainable Extraction:</strong> Pumping exceeds natural recharge by {Math.abs(netChange)}m/year.
                Aquifer depletion will continue unless pumping is reduced or recharge is enhanced.
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
              dataKey="year"
              label={{ value: 'Years', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Depth to Water Table (meters)', angle: -90, position: 'insideLeft' }}
              domain={[0, 80]}
              reversed
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded shadow">
                      <p className="text-sm font-semibold">Year {data.year}</p>
                      <p className="text-sm">Depth: {data.depth}m below surface</p>
                      <p className="text-sm">Change: {data.net_change > 0 ? '+' : ''}{data.net_change}m/yr</p>
                      <p className="text-sm capitalize">Status: {data.status}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <ReferenceLine y={20} stroke="#10b981" strokeDasharray="3 3" label="Healthy" />
            <ReferenceLine y={40} stroke="#f59e0b" strokeDasharray="3 3" label="Concern" />
            <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="3 3" label="Critical" />
            <Line
              type="monotone"
              dataKey="depth"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Depth to Water Table (m)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Recharge Enhancement Options */}
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <h4 className="font-semibold text-sm mb-3">💧 Recharge Enhancement Options:</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="bg-white p-3 rounded">
            <strong className="text-green-600">Managed Aquifer Recharge (MAR)</strong>
            <p className="text-gray-600 mt-1">Inject treated surface water during wet periods</p>
          </div>
          <div className="bg-white p-3 rounded">
            <strong className="text-blue-600">Riparian Restoration</strong>
            <p className="text-gray-600 mt-1">Native vegetation increases infiltration</p>
          </div>
          <div className="bg-white p-3 rounded">
            <strong className="text-purple-600">Land Use Change</strong>
            <p className="text-gray-600 mt-1">Reduce impervious surfaces, increase permeability</p>
          </div>
        </div>
      </div>

      {/* Educational Note */}
      <div className="bg-indigo-50 p-4 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>💡 Systems Thinking:</strong> Aquifers are <em>slow variables</em> in panarchy theory - they operate on
          decadal timescales. This creates a dangerous <em>delay</em>: today's over-pumping won't show effects for years,
          making problems invisible until too late. Notice the <em>stock-flow dynamics</em>: aquifer level (stock) changes
          based on inflow (recharge) minus outflow (pumping). Recovery is asymmetric - depletion happens fast, recovery
          takes decades. This is a classic <em>tragedy of the commons</em> - individual farmers have incentive to pump,
          but collective over-use depletes the shared resource.
        </p>
      </div>
    </div>
  );
};

export default AquiferDrawdownModel;
