import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon } from 'react-leaflet';
import L from 'leaflet';
import taranakiGeoJSON from '../data/taranaki.json';

// Fix for default Leaflet icons in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Site {
  name: string;
  latitude: number;
  longitude: number;
  region: string;
}

interface Measurement {
  name: string;
  units: string;
  datasource: string;
}

interface SiteData {
  site: string;
  measurement: string;
  units: string;
  data: { timestamp: string; value: number }[];
}

const SitePopup: React.FC<{ site: Site }> = ({ site }) => {
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMeasurement, setSelectedMeasurement] = useState<string | null>(null);
  const [siteData, setSiteData] = useState<SiteData | null>(null);
  const [dataLoading, setDataLoading] = useState(false);

  useEffect(() => {
    const fetchMeasurements = async () => {
      try {
        const res = await fetch(`http://localhost:9100/api/public/hilltop/measurements?site=${encodeURIComponent(site.name)}`);
        if (res.ok) {
          const data = await res.json();
          setMeasurements(data.measurements);
          if (data.measurements.length > 0) {
            // Auto-select first interesting measurement (Rainfall or Flow)
            const preferred = data.measurements.find((m: Measurement) => m.name.includes('Rainfall') || m.name.includes('Flow')) || data.measurements[0];
            setSelectedMeasurement(preferred.name);
          }
        }
      } catch (e) {
        console.error("Failed to fetch measurements", e);
      } finally {
        setLoading(false);
      }
    };
    fetchMeasurements();
  }, [site.name]);

  useEffect(() => {
    if (!selectedMeasurement) return;
    
    const fetchData = async () => {
      setDataLoading(true);
      try {
        const res = await fetch(`http://localhost:9100/api/public/hilltop/data?site=${encodeURIComponent(site.name)}&measurement=${encodeURIComponent(selectedMeasurement)}&days=3`);
        if (res.ok) {
          const data = await res.json();
          setSiteData(data);
        }
      } catch (e) {
        console.error("Failed to fetch data", e);
      } finally {
        setDataLoading(false);
      }
    };
    fetchData();
  }, [site.name, selectedMeasurement]);

  return (
    <div className="min-w-[250px]">
      <h3 className="font-bold text-lg border-b pb-1 mb-2">{site.name}</h3>
      
      {loading ? (
        <div className="text-sm text-slate-500">Loading available metrics...</div>
      ) : (
        <div className="space-y-3">
          <select 
            className="w-full text-sm border rounded p-1 bg-slate-50"
            value={selectedMeasurement || ''}
            onChange={(e) => setSelectedMeasurement(e.target.value)}
          >
            {measurements.map(m => (
              <option key={m.name} value={m.name}>{m.name} ({m.units})</option>
            ))}
          </select>

          {dataLoading ? (
            <div className="h-20 flex items-center justify-center text-xs text-slate-400">Fetching data...</div>
          ) : siteData && siteData.data.length > 0 ? (
            <div className="bg-slate-50 p-2 rounded border">
              <div className="text-xs text-slate-500 mb-1">Latest Reading</div>
              <div className="text-2xl font-bold text-blue-600">
                {siteData.data[siteData.data.length - 1].value.toFixed(2)} 
                <span className="text-sm font-normal text-slate-600 ml-1">{siteData.units}</span>
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                {new Date(siteData.data[siteData.data.length - 1].timestamp).toLocaleString()}
              </div>
            </div>
          ) : (
            <div className="text-xs text-red-400">No recent data available</div>
          )}
        </div>
      )}
    </div>
  );
};

const TRCMap: React.FC = () => {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  // Taranaki Polygon coordinates (lat, lon) - reversed from GeoJSON (lon, lat)
  const taranakiBoundary = taranakiGeoJSON.features[0].geometry.coordinates[0].map(
    coord => [coord[1], coord[0]] as [number, number]
  );

  if (loading) return <div className="p-8 text-center text-slate-500">Loading Map Data...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Error loading map: {error}</div>;

  return (
    <div className="h-screen w-full flex flex-col">
      <div className="bg-white p-4 shadow-sm z-10 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Taranaki Environmental Monitoring</h1>
          <p className="text-sm text-slate-500">Real-time data from {sites.length} TRC Hilltop sites</p>
        </div>
        <div className="text-xs text-slate-400">
          Click a marker to view live telemetry
        </div>
      </div>
      
      <div className="flex-1 relative">
        <MapContainer 
          center={[-39.3, 174.3]} 
          zoom={9} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Taranaki Region Overlay */}
          <Polygon 
            positions={taranakiBoundary}
            pathOptions={{ color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, weight: 2 }} 
          />

          {sites.map((site, idx) => (
            <Marker key={idx} position={[site.latitude, site.longitude]}>
              <Popup>
                <SitePopup site={site} />
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default TRCMap;
