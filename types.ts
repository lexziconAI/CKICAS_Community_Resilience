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

// User and Trigger Management Types
export interface User {
  id: string;
  name: string;
  email: string;
  organization: string;
  region: string;
}

export type TriggerIndicator = 'temp' | 'rainfall' | 'humidity' | 'wind_speed';
export type TriggerOperator = '>' | '<' | '>=' | '<=' | '==';
export type CombinationRule = 'any_1' | 'any_2' | 'any_3' | 'all';

export interface TriggerCondition {
  indicator: TriggerIndicator;
  operator: TriggerOperator;
  threshold: number;
}

export interface Trigger {
  id: string;
  user_id: string;
  name: string;
  region: string;
  conditions: TriggerCondition[];
  combination_rule: CombinationRule;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTriggerRequest {
  user_id: string;
  name: string;
  region: string;
  conditions: TriggerCondition[];
  combination_rule: CombinationRule;
  is_active?: boolean;
}

export interface UpdateTriggerRequest {
  name?: string;
  region?: string;
  conditions?: TriggerCondition[];
  combination_rule?: CombinationRule;
  is_active?: boolean;
}

export interface TriggerFormData {
  name: string;
  region: string;
  conditions: TriggerCondition[];
  combination_rule: CombinationRule;
  is_active: boolean;
}