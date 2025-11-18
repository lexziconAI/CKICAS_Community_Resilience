export interface Region {
  name: string;
  lat: number;
  lon: number;
  baseRisk: number;
}

export interface DroughtRiskData {
  region: string;
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  factors: {
    rainfall_deficit: number;
    soil_moisture_index: number;
    temperature_anomaly: number;
  };
  extended_metrics?: {
    wind_speed: number;
    humidity: number;
    pressure: number;
    uv_index?: number;
    weather_main?: string;
  };
  data_source: string;
  last_updated: string;
}

export interface HistoricalDataPoint {
  date: string;
  risk_score: number;
  soil_moisture: number;
  temp: number;
  rain_probability: number;
}

export interface RssFeedItem {
  title: string;
  link: string;
  source: string;
  published: string;
  summary?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ApiStatus {
  status: 'online' | 'offline' | 'checking';
  latency_ms: number;
}

export interface DataSource {
  name: string;
  status: 'active' | 'inactive';
  last_sync: string;
}