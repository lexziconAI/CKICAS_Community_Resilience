import React from 'react';
import { Link } from 'react-router-dom';
import SoilMoistureSimulator from '../components/SoilMoistureSimulator';
import RainfallExplorer from '../components/RainfallExplorer';
import WaterRestrictionCalculator from '../components/WaterRestrictionCalculator';
import IrrigationEfficiencyOptimizer from '../components/IrrigationEfficiencyOptimizer';
import PanarchyNestVisualizer from '../components/PanarchyNestVisualizer';
import AquiferDrawdownModel from '../components/AquiferDrawdownModel';

const SystemDynamics: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link to="/" className="font-bold text-xl text-slate-900 tracking-tight hover:text-blue-600 transition-colors">
              CKCIAS <span className="text-slate-500 font-normal">Drought Monitor</span>
            </Link>
            <span className="text-slate-300">/</span>
            <h2 className="font-semibold text-slate-700">System Dynamics</h2>
          </div>
          <Link
            to="/"
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">System Dynamics Simulators</h1>
          <p className="text-slate-600">
            Interactive models exploring drought system behavior over time. Each simulator shows feedback loops,
            thresholds, delays, and cross-scale effects. All calculations based on empirical data and established models.
          </p>
        </div>

        {/* System Thinking Note */}
        <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-lg mb-8">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-indigo-800">Systems Thinking Approach</h3>
              <p className="text-sm text-indigo-700 mt-1">
                These simulators reveal how drought systems operate through <em>feedback loops</em> (reinforcing and balancing),
                <em>time delays</em> (actions today impact future states), <em>thresholds</em> (non-linear behavior changes),
                <em>stock-flow dynamics</em> (accumulation and depletion), and <em>nested scales</em> (fast farm decisions
                embedded in slow regional/national cycles). Understanding these patterns helps identify high-leverage intervention points.
              </p>
            </div>
          </div>
        </div>

        {/* Simulators Grid */}
        <div className="space-y-8">
          {/* Row 1: Fast Variables (Hours to Days) */}
          <div>
            <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="text-green-500">⚡</span>
              Fast Variables (Hours to Days)
            </h2>
            <div className="grid grid-cols-1 gap-6">
              <SoilMoistureSimulator />
            </div>
          </div>

          {/* Row 2: Medium Variables (Weeks to Months) */}
          <div>
            <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="text-blue-500">🌊</span>
              Medium Variables (Weeks to Months)
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RainfallExplorer />
              <WaterRestrictionCalculator />
            </div>
          </div>

          {/* Row 3: Management & Efficiency */}
          <div>
            <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="text-orange-500">🚜</span>
              Management & Efficiency
            </h2>
            <div className="grid grid-cols-1 gap-6">
              <IrrigationEfficiencyOptimizer />
            </div>
          </div>

          {/* Row 4: Slow Variables & Cross-Scale (Years to Decades) */}
          <div>
            <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
              <span className="text-purple-500">🔮</span>
              Slow Variables & Cross-Scale (Years to Decades)
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PanarchyNestVisualizer />
              <AquiferDrawdownModel />
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mt-8">
          <h3 className="font-semibold text-slate-800 mb-3">About These Models</h3>
          <div className="space-y-2 text-sm text-slate-600">
            <p>
              <strong>Data Sources:</strong> All models use empirical data from established sources (e.g., Penman-Monteith ET equations,
              NZ irrigation efficiency standards, real aquifer characteristics). No mock data - only calculations and projections
              based on real parameters.
            </p>
            <p>
              <strong>Educational Purpose:</strong> These simulators are designed to build intuition about drought system dynamics.
              They simplify complex reality to highlight key patterns. For operational decisions, consult professional hydrologists
              and water resource managers.
            </p>
            <p>
              <strong>Theoretical Foundation:</strong> Based on systems thinking frameworks including System Dynamics (Forrester),
              Panarchy Theory (Holling & Gunderson), and resilience science. Each model includes explanatory notes linking theory to practice.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SystemDynamics;
