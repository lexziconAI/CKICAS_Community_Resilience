import React, { useEffect, useState } from 'react';

interface Site {
  name: string;
  latitude: number;
  longitude: number;
  region: string;
}

const TRCMap: React.FC = () => {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const response = await fetch('http://localhost:9100/api/public/hilltop/sites');
        if (!response.ok) throw new Error('Failed to fetch sites');
        const data = await response.json();
        setSites(data.sites);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    fetchSites();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-slate-100 rounded-lg">
        <div className="text-slate-600">Loading Taranaki monitoring sites...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96 bg-red-50 rounded-lg">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  // Simple coordinate-to-pixel mapping for NZ (Taranaki region)
  // Lat range: -39.1 to -39.8, Lon range: 173.8 to 174.6
  const latMin = -39.8, latMax = -39.1;
  const lonMin = 173.8, lonMax = 174.6;
  const width = 800, height = 600;

  const latToY = (lat: number) => ((latMax - lat) / (latMax - latMin)) * height;
  const lonToX = (lon: number) => ((lon - lonMin) / (lonMax - lonMin)) * width;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4 text-slate-800">
        Taranaki Regional Council - Monitoring Sites
      </h2>
      <div className="text-sm text-slate-600 mb-4">
        {sites.length} active monitoring stations
      </div>

      <div className="relative bg-gradient-to-br from-blue-50 to-green-50 rounded-lg overflow-hidden border-2 border-slate-300">
        <svg width={width} height={height} className="w-full h-auto">
          {/* Grid lines */}
          <g opacity="0.2">
            {[...Array(10)].map((_, i) => (
              <React.Fragment key={i}>
                <line x1={0} y1={i * 60} x2={width} y2={i * 60} stroke="#94a3b8" strokeWidth="1" />
                <line x1={i * 80} y1={0} x2={i * 80} y2={height} stroke="#94a3b8" strokeWidth="1" />
              </React.Fragment>
            ))}
          </g>

          {/* Site markers */}
          {sites.map((site, idx) => {
            const x = lonToX(site.longitude);
            const y = latToY(site.latitude);

            return (
              <g key={idx} onClick={() => setSelectedSite(site)} style={{ cursor: 'pointer' }}>
                <circle
                  cx={x}
                  cy={y}
                  r={selectedSite?.name === site.name ? 8 : 6}
                  fill={selectedSite?.name === site.name ? "#f59e0b" : "#3b82f6"}
                  stroke={selectedSite?.name === site.name ? "#d97706" : "#1e40af"}
                  strokeWidth="2"
                  className="transition-all"
                  opacity="0.9"
                >
                  <title>{site.name}</title>
                </circle>
                <circle
                  cx={x}
                  cy={y}
                  r="12"
                  fill={selectedSite?.name === site.name ? "#f59e0b" : "#3b82f6"}
                  opacity="0.2"
                  className="animate-ping"
                  style={{ animationDuration: `${2 + (idx % 3)}s` }}
                />
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-3 h-3 rounded-full bg-blue-500 border-2 border-blue-800"></div>
            <span className="text-slate-700 font-medium">Monitoring Station</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Flow, Stage, Water Quality
          </div>
        </div>

        {/* Compass */}
        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
          <div className="text-xs font-bold text-slate-700">N ↑</div>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-500">
        Data source: Taranaki Regional Council Hilltop Server • Real-time environmental monitoring
      </div>

      {/* Site List */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3 text-slate-800">Monitoring Sites ({sites.length})</h3>
        <div className="max-h-96 overflow-y-auto bg-slate-50 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {sites.map((site, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedSite(site)}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedSite?.name === site.name
                    ? 'bg-amber-100 border-2 border-amber-500'
                    : 'bg-white border border-slate-200 hover:border-blue-400 hover:shadow-md'
                }`}
              >
                <div className="font-medium text-sm text-slate-900">{site.name}</div>
                <div className="text-xs text-slate-500 mt-1">
                  Lat: {site.latitude.toFixed(4)}, Lon: {site.longitude.toFixed(4)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TRCMap;
