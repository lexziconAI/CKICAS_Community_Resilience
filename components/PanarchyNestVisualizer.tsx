import React, { useState } from 'react';

interface PanarchyScale {
  name: string;
  speed: string;
  timeScale: string;
  examples: string[];
  variables: string[];
  color: string;
}

const PanarchyNestVisualizer: React.FC = () => {
  const [selectedScale, setSelectedScale] = useState<number>(1);

  const scales: PanarchyScale[] = [
    {
      name: 'Farm (Fast)',
      speed: 'Hours to Days',
      timeScale: 'Daily Decisions',
      examples: [
        'Check soil moisture',
        'Turn on irrigation',
        'Move stock between paddocks',
        'Daily weather checks'
      ],
      variables: ['Soil Moisture', 'Daily Rainfall', 'Pasture Cover', 'Stock Water Needs'],
      color: '#10b981' // green
    },
    {
      name: 'Regional (Medium)',
      speed: 'Weeks to Months',
      timeScale: 'Seasonal Management',
      examples: [
        'Council water restrictions',
        'Dam level monitoring',
        'Regional drought declarations',
        'Community water allocation'
      ],
      variables: ['Dam Levels', 'River Flows', 'Aquifer Recharge', 'Regional Rainfall'],
      color: '#3b82f6' // blue
    },
    {
      name: 'National (Slow)',
      speed: 'Years to Decades',
      timeScale: 'Policy & Climate',
      examples: [
        'Climate change adaptation',
        'Water allocation frameworks',
        'Infrastructure investment',
        'Land use change'
      ],
      variables: ['Aquifer Capacity', 'Climate Trends', 'Policy Frameworks', 'Infrastructure'],
      color: '#8b5cf6' // purple
    }
  ];

  const current = scales[selectedScale];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">🌀 Panarchy: Nested Adaptive Cycles</h3>
        <p className="text-sm text-gray-600">
          Drought systems operate at multiple nested scales - fast farm decisions embedded in slower regional/national cycles.
        </p>
      </div>

      {/* Nested Circles Visualization */}
      <div className="flex justify-center mb-8">
        <div className="relative w-80 h-80">
          {/* Outer Circle - National */}
          <div
            onClick={() => setSelectedScale(2)}
            className={`absolute inset-0 rounded-full border-8 flex items-center justify-center cursor-pointer transition-all ${
              selectedScale === 2 ? 'border-purple-500 bg-purple-50' : 'border-purple-300 bg-white hover:bg-purple-50'
            }`}
            style={{ animation: 'spin 60s linear infinite' }}
          >
            <span className={`text-sm font-semibold ${selectedScale === 2 ? 'text-purple-700' : 'text-purple-500'}`}>
              National (Slow)
            </span>

            {/* Middle Circle - Regional */}
            <div
              onClick={(e) => { e.stopPropagation(); setSelectedScale(1); }}
              className={`absolute inset-12 rounded-full border-8 flex items-center justify-center cursor-pointer transition-all ${
                selectedScale === 1 ? 'border-blue-500 bg-blue-50' : 'border-blue-300 bg-white hover:bg-blue-50'
              }`}
              style={{ animation: 'spin 30s linear infinite' }}
            >
              <span className={`text-sm font-semibold ${selectedScale === 1 ? 'text-blue-700' : 'text-blue-500'}`}>
                Regional (Medium)
              </span>

              {/* Inner Circle - Farm */}
              <div
                onClick={(e) => { e.stopPropagation(); setSelectedScale(0); }}
                className={`absolute inset-12 rounded-full border-8 flex items-center justify-center cursor-pointer transition-all ${
                  selectedScale === 0 ? 'border-green-500 bg-green-50' : 'border-green-300 bg-white hover:bg-green-50'
                }`}
                style={{ animation: 'spin 10s linear infinite' }}
              >
                <span className={`text-sm font-semibold ${selectedScale === 0 ? 'text-green-700' : 'text-green-500'}`}>
                  Farm (Fast)
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Scale Details */}
      <div className={`border-4 rounded-lg p-6 mb-6`} style={{ borderColor: current.color }}>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-bold" style={{ color: current.color }}>{current.name}</h4>
          <div className="text-right">
            <div className="text-xs text-gray-600">Time Scale</div>
            <div className="text-sm font-semibold">{current.speed}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2">Key Variables:</h5>
            <ul className="space-y-1">
              {current.variables.map((variable, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start">
                  <span className="text-xl mr-2">•</span>
                  <span>{variable}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h5 className="text-sm font-semibold text-gray-700 mb-2">Example Activities:</h5>
            <ul className="space-y-1">
              {current.examples.map((example, idx) => (
                <li key={idx} className="text-sm text-gray-600 flex items-start">
                  <span className="text-xl mr-2">→</span>
                  <span>{example}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Cross-Scale Effects */}
      <div className="bg-gradient-to-r from-green-50 via-blue-50 to-purple-50 p-4 rounded-lg mb-4">
        <h4 className="font-semibold text-sm mb-3">🔄 Cross-Scale Dynamics:</h4>
        <div className="space-y-2 text-sm text-gray-700">
          <div className="flex items-start">
            <span className="text-green-500 font-bold mr-2">↗</span>
            <span><strong>Revolts (Fast → Slow):</strong> Farm-level drought stress aggregates to trigger regional restrictions,
              which can influence national policy changes.</span>
          </div>
          <div className="flex items-start">
            <span className="text-purple-500 font-bold mr-2">↘</span>
            <span><strong>Remembers (Slow → Fast):</strong> National water allocation frameworks and aquifer capacity
              constrain regional policy options, which limit farm choices.</span>
          </div>
        </div>
      </div>

      {/* Adaptive Cycle Phases */}
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <h4 className="font-semibold text-sm mb-3">♻️ Adaptive Cycle Phases (all scales):</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="bg-white p-3 rounded">
            <div className="font-bold text-green-600">Growth (r)</div>
            <div className="text-gray-600 mt-1">Resource accumulation, expansion</div>
          </div>
          <div className="bg-white p-3 rounded">
            <div className="font-bold text-blue-600">Conservation (K)</div>
            <div className="text-gray-600 mt-1">Stability, optimization, rigidity</div>
          </div>
          <div className="bg-white p-3 rounded">
            <div className="font-bold text-orange-600">Release (Ω)</div>
            <div className="text-gray-600 mt-1">Collapse, disruption, crisis</div>
          </div>
          <div className="bg-white p-3 rounded">
            <div className="font-bold text-purple-600">Reorganization (α)</div>
            <div className="text-gray-600 mt-1">Innovation, adaptation, renewal</div>
          </div>
        </div>
      </div>

      {/* Educational Note */}
      <div className="bg-yellow-50 p-4 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>💡 Systems Thinking:</strong> <em>Panarchy</em> (Holling & Gunderson) shows how systems at different
          speeds interact. Fast variables (daily soil moisture) are constrained by slow variables (aquifer levels). But fast
          changes can also cascade upward - many farms in crisis triggers regional response. Understanding these nested cycles
          helps target interventions: farm-level efficiency (fast), regional restrictions (medium), or infrastructure investment (slow).
          All three scales must be addressed for resilience.
        </p>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default PanarchyNestVisualizer;
