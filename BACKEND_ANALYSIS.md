# CKICAS Drought Monitor - Python Backend Analysis

## Overview
The CKICAS Drought Monitor is a New Zealand-focused drought monitoring and risk assessment system with an AI-powered chatbot interface. The backend is built with FastAPI and provides real-time drought risk calculations, weather data integration, and AI-powered analysis using Google Gemini.

## Backend Architecture

### Framework & Stack
- **Framework**: FastAPI (>= 0.100.0)
- **Server**: Uvicorn (>= 0.22.0)
- **Language**: Python 3.11+
- **Port**: 9100
- **AI Model**: Google Gemini (via google-generativeai >= 0.3.0)

### Dependencies (requirements.txt)
```
fastapi>=0.100.0              # Web framework
uvicorn>=0.22.0               # ASGI server
python-dotenv>=1.0.0          # Environment variable management
google-generativeai>=0.3.0    # Google Gemini AI integration
httpx>=0.24.0                 # HTTP client for external API calls
pydantic>=2.0.0               # Data validation & serialization
feedparser>=6.0.10            # RSS feed parsing for council alerts
beautifulsoup4>=4.12.0        # HTML parsing for council alerts
```

---

## API Endpoints (Inferred from Frontend)

### 1. Health Check
**Endpoint**: `GET /health`
- **Purpose**: Check if backend server is running
- **Response**: Simple 200 OK status
- **Used by**: Frontend `checkApiHealth()` to determine if backend is online vs offline vs serverless

### 2. Drought Risk Calculation
**Endpoint**: `GET /api/public/drought-risk`
**Query Parameters**:
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate  
- `region` (string): Region name (e.g., "Canterbury", "Waikato")

**Response**: DroughtRiskData JSON
```json
{
  "region": "Canterbury",
  "risk_score": 65,
  "risk_level": "High",
  "factors": {
    "rainfall_deficit": 45.2,
    "soil_moisture_index": 35,
    "temperature_anomaly": 2.5
  },
  "extended_metrics": {
    "wind_speed": 12.4,
    "humidity": 68,
    "pressure": 1013,
    "weather_main": "Partly Cloudy"
  },
  "data_source": "OpenWeatherMap (Live Client) | NIWA DataHub | Backend API",
  "last_updated": "2025-11-19T10:30:00Z"
}
```

### 3. Forecast Trend Data
**Endpoint**: `GET /api/public/forecast-trend`
**Query Parameters**:
- `lat` (float): Latitude
- `lon` (float): Longitude

**Response**: Array of HistoricalDataPoint
```json
[
  {
    "date": "Mon",
    "risk_score": 42.5,
    "soil_moisture": 58.3,
    "temp": 16.2,
    "rain_probability": 25.0
  },
  // ... 6 more days of forecast
]
```

### 4. Council Alerts (RSS Feeds)
**Endpoint**: `GET /api/public/council-alerts`

**Response**: Array of RssFeedItem
```json
[
  {
    "title": "Water Use Restrictions - Stage 2",
    "link": "https://council.example.com/alert/123",
    "source": "Canterbury Council",
    "published": "2025-11-18T09:00:00Z",
    "summary": "Stage 2 water restrictions now in effect for the Canterbury region..."
  }
]
```

### 5. Data Sources Status
**Endpoint**: `GET /api/public/data-sources`

**Response**: Array of DataSource
```json
[
  {
    "name": "NIWA DataHub",
    "status": "active|inactive",
    "last_sync": "2025-11-19T10:25:00Z | Backend Offline"
  },
  {
    "name": "OpenWeatherMap",
    "status": "active",
    "last_sync": "2025-11-19T10:30:00Z"
  },
  {
    "name": "Regional Councils",
    "status": "active",
    "last_sync": "2025-11-19T09:15:00Z"
  }
]
```

### 6. Chat/AI Analysis
**Endpoint**: `POST /api/chat`

**Request Body**:
```json
{
  "message": "Tell me about drought conditions in Canterbury"
}
```

**Response**:
```json
{
  "response": "Canterbury is experiencing high drought risk (65/100) with..."
}
```

---

## Drought Risk Calculation Logic

### Risk Score Calculation (inferred from frontend fallback logic)

The drought risk is calculated using multiple environmental factors:

```
Base Risk Score = Region.baseRisk (pre-defined per region, 15-65)

Adjustments:
1. Temperature Anomaly Impact
   - Baseline Temperature: 15.0°C
   - Deviation Factor: +2.0 per °C above baseline
   - Example: 18°C = +6 points to risk

2. Humidity/Rainfall Deficit Impact
   - Target Humidity: 80%
   - Humidity Deficit = max(0, 80 - current_humidity)
   - Impact Factor: +0.5 per point of deficit
   - Example: 68% humidity = 12 point deficit × 0.5 = +6 points

3. Final Risk Score:
   risk_score = base_risk + (temp_anomaly × 2.0) + (humidity_deficit × 0.5)
   risk_score = max(5, min(99, floor(risk_score)))
```

### Risk Level Classification

| Risk Score | Risk Level | Color     | Interpretation |
|------------|-----------|----------|-----------------|
| 0-25      | Low       | Green    | Favorable conditions |
| 26-50     | Medium    | Yellow   | Moderate concern |
| 51-75     | High      | Orange   | Significant risk |
| 76-100    | Critical  | Red      | Severe drought threat |

### Factors Calculated

1. **Rainfall Deficit**: Percentage deviation from target humidity (80%)
   - Higher values = More water stress
   - Range: 0-100%

2. **Soil Moisture Index**: Inverse of risk score
   - soil_moisture_index = 100 - risk_score
   - Higher = Better moisture retention

3. **Temperature Anomaly**: Deviation from 15°C baseline
   - Positive = Warmer than normal (increases evaporation)
   - Negative = Cooler than normal (decreases risk)
   - Units: °C

### Regional Base Risk Scores (NZ Regions)

Dry regions (High Base Risk):
- Canterbury: 65 (driest region)
- Gisborne: 62
- Hawke's Bay: 58
- Otago: 55
- Waikato: 55

Moderate regions:
- Marlborough: 48
- Manawatu-Wanganui: 42
- Taranaki: 38

Wet/Coastal regions (Low Base Risk):
- West Coast: 20
- Northland: 25
- Wellington: 28
- Tasman: 35

---

## Weather Data Integration

### Primary Source: OpenWeatherMap API
- **API Endpoint**: https://api.openweathermap.org/data/2.5/weather
- **API Key**: Required (d7ab6944b5791f6c502a506a6049165f for fallback)
- **Parameters**: lat, lon, appid, units=metric
- **Data Retrieved**:
  - Current temperature
  - Humidity percentage
  - Pressure (hPa)
  - Wind speed (m/s)
  - Weather condition (main)

### Secondary Sources (Backend only when operational)
1. **NIWA DataHub**
   - New Zealand-specific meteorological data
   - Historical drought indices
   - Soil moisture measurements

2. **Regional Council RSS Feeds**
   - Current water use restrictions
   - Drought alerts and warnings
   - Public advisories

3. **Forecast Data**
   - 7-day forecast trends
   - Rain probability
   - Temperature projections

---

## Chatbot Functionality & AI Integration

### Chatbot Architecture

**Primary Model**: Google Gemini 2.5 Flash (via google-generativeai)
**Configuration**:
- Model: `gemini-2.5-flash`
- Fallback Model: `gemini-1.5-pro` or similar

### System Instruction (Prompt Engineering)

```
"You are the CKICAS Drought Monitor AI Assistant for New Zealand. 
Provide concise, expert advice on drought risk, rainfall, and soil moisture 
for NZ farmers. Only base your advice on general knowledge if specific 
real-time data is unavailable."
```

### Capabilities

1. **Drought Analysis**
   - Risk assessment for specific regions
   - Trend analysis and predictions
   - Comparison across regions

2. **Agricultural Advice**
   - Water management recommendations
   - Crop-specific drought strategies
   - Irrigation planning

3. **Information Retrieval**
   - Regional drought statistics
   - Historical trends
   - Current alert status

4. **Natural Language Understanding**
   - Multi-turn conversation support
   - Context awareness
   - Regional disambiguation

### Fallback Strategy (Client-Side)

If backend is offline:
1. Frontend checks for GOOGLE_API_KEY and OPENWEATHER_API_KEY
2. If available, uses Gemini directly from browser (client-side)
3. Model: `gemini-2.5-flash` or `gemini-1.5` equivalent
4. Operates in "serverless" mode status

---

## External Services & APIs Used

### 1. Google Gemini AI
- **Service**: Generative AI for chatbot
- **Authentication**: API Key (GOOGLE_API_KEY environment variable)
- **Models**: 
  - Primary: gemini-2.5-flash
  - Secondary: gemini-1.5-pro
- **Purpose**: Natural language analysis and advice generation
- **Fallback**: Client-side execution when backend unavailable

### 2. OpenWeatherMap
- **Service**: Real-time weather data
- **Authentication**: API Key (OPENWEATHER_API_KEY)
- **Endpoint**: api.openweathermap.org/data/2.5/weather
- **Purpose**: Current temperature, humidity, wind, pressure
- **Caching**: Frontend implements client-side fallback

### 3. NIWA DataHub (Backend only)
- **Purpose**: New Zealand meteorological data
- **Data**: Official drought indices, soil moisture
- **Integration**: RSS feeds or REST API
- **Status**: Optional but recommended

### 4. Regional Council Systems
- **Purpose**: Water restrictions and alerts
- **Format**: RSS feeds
- **Integration**: feedparser library
- **Coverage**: All 16 NZ regions

---

## Data Flow & Processing Logic

### Diagram: Request-Response Flow

```
Frontend (React/Vite)
    |
    |-- Checks /health endpoint
    |
    |-- GET /api/public/drought-risk?lat=X&lon=Y&region=Name
    |   |
    |   Backend (FastAPI)
    |   |-- Queries OpenWeatherMap API
    |   |-- Calculates risk_score using algorithm
    |   |-- Returns DroughtRiskData
    |   |
    |   Frontend receives:
    |   - Risk score & level
    |   - Factors (rainfall, soil moisture, temp)
    |   - Extended metrics (wind, humidity, pressure)
    |
    |-- GET /api/public/forecast-trend?lat=X&lon=Y
    |   |
    |   Backend
    |   |-- Fetches 7-day forecast from OpenWeatherMap
    |   |-- Calculates daily risk projections
    |   |-- Returns historical trend data
    |   |
    |   Frontend displays:
    |   - Line chart with risk/moisture trends
    |   - Rain probability
    |
    |-- GET /api/public/council-alerts
    |   |
    |   Backend
    |   |-- Parses regional council RSS feeds
    |   |-- Filters recent alerts
    |   |-- Returns formatted alerts
    |   |
    |   Frontend displays:
    |   - Notification banner
    |   - Alert details in separate panel
    |
    |-- POST /api/chat (message: string)
    |   |
    |   Backend
    |   |-- Receives user message
    |   |-- Calls Google Gemini API
    |   |-- Sends system instruction + context
    |   |-- Returns AI response
    |   |
    |   Frontend displays:
    |   - Assistant response in chat
    |   - Streaming support (optional)
```

### Step-by-Step Processing: Drought Risk Request

1. **User clicks region on map**
   - Frontend has: latitude, longitude, region name

2. **Frontend sends request**
   - `GET /api/public/drought-risk?lat=-43.5&lon=171.2&region=Canterbury`

3. **Backend processes**
   ```python
   # 1. Receive parameters
   lat, lon, region = parse_request()
   
   # 2. Fetch current weather
   weather = openweathermap.get_weather(lat, lon)
   temp = weather['main']['temp']
   humidity = weather['main']['humidity']
   
   # 3. Calculate risk
   base_risk = get_regional_base_risk(region)  # e.g., 65 for Canterbury
   temp_anomaly = temp - 15.0  # e.g., 18°C - 15°C = 3°C
   humidity_deficit = max(0, 80 - humidity)  # e.g., 80 - 68 = 12
   
   risk_score = base_risk + (temp_anomaly * 2.0) + (humidity_deficit * 0.5)
   # = 65 + (3 * 2.0) + (12 * 0.5)
   # = 65 + 6 + 6 = 77
   
   # 4. Determine risk level
   risk_level = get_risk_level(risk_score)  # "High" or "Critical"
   
   # 5. Extract factors
   soil_moisture_index = 100 - risk_score  # 100 - 77 = 23
   rainfall_deficit = humidity_deficit  # 12
   
   # 6. Format response
   response = {
     "region": region,
     "risk_score": risk_score,
     "risk_level": risk_level,
     "factors": {
       "rainfall_deficit": rainfall_deficit,
       "soil_moisture_index": soil_moisture_index,
       "temperature_anomaly": temp_anomaly
     },
     "extended_metrics": {
       "wind_speed": weather['wind']['speed'],
       "humidity": humidity,
       "pressure": weather['main']['pressure'],
       "weather_main": weather['weather'][0]['main']
     },
     "data_source": "OpenWeatherMap (Live Client)",
     "last_updated": current_timestamp()
   }
   ```

4. **Frontend receives and displays**
   - Shows risk score with color-coded visual
   - Updates map marker color
   - Populates weather metrics panel
   - Enables chat for that region

### Chat Processing Flow

1. **User submits message in chat interface**
   - Message: "Tell me about drought in Canterbury"

2. **Frontend sends to backend**
   ```
   POST /api/chat
   {
     "message": "Tell me about drought in Canterbury"
   }
   ```

3. **Backend processes**
   ```python
   # 1. Receive message
   user_message = request.body['message']
   
   # 2. Call Google Gemini
   genai_client = initialize_gemini_client(GOOGLE_API_KEY)
   
   response = genai_client.models.generateContent({
     "model": "gemini-2.5-flash",
     "contents": user_message,
     "config": {
       "systemInstruction": "You are CKICAS Drought Monitor AI..."
     }
   })
   
   # 3. Extract response text
   ai_response = response.text
   # "Canterbury is experiencing high drought risk (65/100) due to..."
   
   # 4. Return to frontend
   return {"response": ai_response}
   ```

4. **Frontend displays response**
   - Renders in chat bubble
   - Supports markdown (bold, lists)
   - Auto-scrolls to latest message

---

## Configuration

### Environment Variables (.env)
```
GOOGLE_API_KEY=PLACEHOLDER_API_KEY
OPENWEATHER_API_KEY=d7ab6944b5791f6c502a506a6049165f (fallback)
NIWA_API_KEY=<optional>
```

### Server Configuration
- **Host**: 0.0.0.0
- **Port**: 9100
- **Reload**: Enabled (for development)
- **CORS**: Likely enabled for frontend communication

---

## Key Design Features

### 1. Hybrid Operation Model
- **Online Mode**: Full backend functionality with all data sources
- **Serverless Mode**: Frontend operates independently with Gemini
- **Offline Mode**: Display cached data or graceful degradation

### 2. Fault Tolerance
- Graceful fallbacks to client-side OpenWeatherMap
- Mock data generation if services unavailable
- System status indicators (Online/Offline/Serverless)

### 3. Real-time Data Updates
- Every region loads data in parallel (Promise.all)
- 30-second health check interval for API status
- Last_updated timestamps on all responses

### 4. Scalability Considerations
- Stateless API design (no sessions)
- Caching potential at multiple levels
- Parallel weather API calls

---

## Summary

The CKICAS Drought Monitor backend is a modern FastAPI application that:

1. **Integrates multiple data sources**: OpenWeatherMap, NIWA, Regional Councils
2. **Performs sophisticated risk calculations**: Multi-factor drought risk assessment
3. **Provides AI-powered analysis**: Google Gemini chatbot integration
4. **Operates resilience**: Serverless fallback when backend unavailable
5. **Serves New Zealand**: Tailored regional risk profiles for all 16 NZ regions
6. **Targets farmers**: Practical drought advice and water management guidance

Key endpoints provide drought risk data, trend forecasts, council alerts, and AI-powered chatbot responses, all designed for real-time decision support in agricultural drought management.
