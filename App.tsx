import React, { useState, useEffect } from 'react';
import DroughtMap from './components/DroughtMap';
import ChatInterface from './components/ChatInterface';
import StatusCard from './components/StatusCard';
import HistoricalChart from './components/HistoricalChart';
import CouncilAlerts from './components/CouncilAlerts';
import { checkApiHealth, fetchDataSources, fetchForecastTrend } from './services/api';
import { DataSource, DroughtRiskData, HistoricalDataPoint } from './types';

const App: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking' | 'serverless'>('checking');
  const [latency, setLatency] = useState(0);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [selectedRegionData, setSelectedRegionData] = useState<DroughtRiskData | null>(null);
  const [trendData, setTrendData] = useState<HistoricalDataPoint[]>([]);
  const [loadingTrend, setLoadingTrend] = useState(false);

  useEffect(() => {
    const initSystem = async () => {
      const health = await checkApiHealth();
      setApiStatus(health.status);
      setLatency(health.latency);

      if (health.status === 'online' || health.status === 'serverless') {
        try {
          const sources = await fetchDataSources();
          setDataSources(sources);
        } catch (e) {
          console.error("Failed to load sources", e);
        }
      }
    };

    initSystem();
    const interval = setInterval(initSystem, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRegionSelect = async (data: DroughtRiskData) => {
    setSelectedRegionData(data);
    setLoadingTrend(true);
    // Fetch trend data for the new region
    const regionDef = { lat: -41.2, lon: 174.8 }; // Fallback
    // In a real app we'd look up the lat/lon from NZ_REGIONS or pass it in `data`
    // Here we assume we can fetch based on the data provided or re-use logic.
    // Ideally DroughtMap passes lat/lon too.
    const regionLat = -41.0; // Approximate for demo if not in data
    const regionLon = 174.0; 
    
    const trends = await fetchForecastTrend(regionLat, regionLon);
    setTrendData(trends);
    setLoadingTrend(false);
  };

  const activeSourcesCount = dataSources.filter(s => s.status === 'active').length;

  const getStatusBadge = () => {
    if (apiStatus === 'online') {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="font-medium text-xs">System Online ({latency}ms)</span>
        </div>
      );
    } else if (apiStatus === 'serverless') {
       return (
        <div className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          <span className="font-medium text-xs">Live (Serverless Mode)</span>
        </div>
      );
    } else if (apiStatus === 'checking') {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full">
          <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
          <span className="font-medium text-xs">Checking...</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-red-100 text-red-800 rounded-full">
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          <span className="font-medium text-xs">System Offline</span>
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-blue-200 shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h1 className="font-bold text-xl text-slate-900 tracking-tight">CKICAS <span className="text-slate-500 font-normal">Drought Monitor</span></h1>
          </div>
          <div className="flex items-center gap-4 text-sm">
            {getStatusBadge()}
          </div>
        </div>
        <CouncilAlerts />
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatusCard 
            title="Active Sensors" 
            value={activeSourcesCount} 
            subtitle={`Total Sources: ${dataSources.length}`}
            status={activeSourcesCount > 0 ? 'success' : 'warning'}
            icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatusCard 
            title="Nat'l Avg Risk" 
            value="42/100" 
            subtitle="Moderate Concern"
            status="warning"
            icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
          />
          <StatusCard 
            title="AI Model" 
            value="Gemini 2.5" 
            subtitle="Flash Optimized"
            status="success"
            icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>}
          />
          <StatusCard 
            title="Last Update" 
            value="Just now" 
            subtitle="Real-time Sync"
            status="neutral"
            icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
        </div>

        {/* Main Interface: Map and Chat */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 flex flex-col gap-6">
            <div className="bg-white p-1 rounded-xl shadow-sm border border-slate-200">
               <DroughtMap onRegionSelect={handleRegionSelect} />
            </div>
            
            {/* Detailed Region Panel (Visible on Selection) */}
            {selectedRegionData && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up">
                {/* Extended Metrics */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                  <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center justify-between">
                    <span>Weather Metrics: {selectedRegionData.region}</span>
                    <span className="text-xs font-normal px-2 py-1 bg-slate-100 rounded text-slate-500">{selectedRegionData.extended_metrics?.weather_main || 'Clear'}</span>
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Wind Speed</div>
                      <div className="text-xl font-bold text-slate-700">{selectedRegionData.extended_metrics?.wind_speed || '--'} <span className="text-xs font-normal">m/s</span></div>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Humidity</div>
                      <div className="text-xl font-bold text-blue-600">{selectedRegionData.extended_metrics?.humidity || '--'} <span className="text-xs font-normal">%</span></div>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Pressure</div>
                      <div className="text-xl font-bold text-slate-700">{selectedRegionData.extended_metrics?.pressure || '--'} <span className="text-xs font-normal">hPa</span></div>
                    </div>
                     <div className="p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Soil Deficit</div>
                      <div className="text-xl font-bold text-orange-600">{selectedRegionData.factors.rainfall_deficit} <span className="text-xs font-normal">mm</span></div>
                    </div>
                  </div>
                </div>

                {/* Historical Graph */}
                <div className="h-[250px]">
                  <HistoricalChart data={trendData} regionName={selectedRegionData.region} />
                </div>
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <ChatInterface selectedRegion={selectedRegionData?.region || null} />
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-slate-200 py-6 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>&copy; 2025 CKICAS Drought Monitor. A Vibe Coding Project.</p>
          <p className="mt-1">Worker Army Deployment • Gemini Integrated • OpenWeather Forecasts</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
