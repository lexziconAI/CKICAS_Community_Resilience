# CKICAS Drought Monitor - Backend Implementation Notes

## File Structure & Implementation

### 1. main.py - Server Entry Point

Expected structure and initialization logic:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CKICAS Drought Monitor API",
    description="Real-time drought risk assessment for New Zealand",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from routes import router as api_router
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "online"}

# Startup event
@app.on_event("startup")
async def startup_event():
    print("CKICAS Drought Monitor API starting...")
    # Initialize services, load data, etc.
    pass

# Root endpoint
@app.get("/")
async def root():
    return {"message": "CKICAS Drought Monitor Backend v1.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
    port=9100,
        reload=True  # Development mode
    )
```

**Key Components:**
- CORS configuration for localhost:5173 (React frontend)
- Environment variable loading from .env
- Startup initialization for services
- Health check endpoint for frontend monitoring

---

### 2. routes.py - API Endpoints

Expected endpoint implementations:

```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
import httpx
import os
from datetime import datetime

from weather_service import get_weather_data
from drought_risk import calculate_drought_risk, get_risk_level
from chatbot import chat_with_gemini

router = APIRouter(prefix="/public")

# ============ DATA MODELS (Pydantic) ============

class DroughtFactors(BaseModel):
    rainfall_deficit: float
    soil_moisture_index: float
    temperature_anomaly: float

class ExtendedMetrics(BaseModel):
    wind_speed: float
    humidity: float
    pressure: float
    weather_main: str

class DroughtRiskData(BaseModel):
    region: str
    risk_score: int
    risk_level: str  # "Low", "Medium", "High", "Critical"
    factors: DroughtFactors
    extended_metrics: ExtendedMetrics
    data_source: str
    last_updated: str

class HistoricalDataPoint(BaseModel):
    date: str
    risk_score: float
    soil_moisture: float
    temp: float
    rain_probability: float

class RssFeedItem(BaseModel):
    title: str
    link: str
    source: str
    published: str
    summary: str = ""

class DataSource(BaseModel):
    name: str
    status: str  # "active" or "inactive"
    last_sync: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# ============ ENDPOINTS ============

@router.get("/drought-risk", response_model=DroughtRiskData)
async def get_drought_risk(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    region: str = Query(..., description="Region name")
):
    """
    Calculate drought risk for a specific location.
    
    Query Parameters:
    - lat: Latitude coordinate
    - lon: Longitude coordinate
    - region: Region name (e.g., "Canterbury")
    
    Returns: DroughtRiskData with risk score, level, and factors
    """
    try:
        # Fetch current weather
        weather = await get_weather_data(lat, lon)
        
        # Calculate risk
        risk_score, risk_level, factors = calculate_drought_risk(
            region=region,
            temperature=weather["temp"],
            humidity=weather["humidity"]
        )
        
        # Format response
        return DroughtRiskData(
            region=region,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            extended_metrics=ExtendedMetrics(
                wind_speed=weather["wind_speed"],
                humidity=weather["humidity"],
                pressure=weather["pressure"],
                weather_main=weather["weather_main"]
            ),
            data_source="OpenWeatherMap (Live Client)",
            last_updated=datetime.utcnow().isoformat() + "Z"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast-trend", response_model=List[HistoricalDataPoint])
async def get_forecast_trend(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get 7-day drought risk forecast for a location.
    
    Returns: Array of daily risk scores, temperatures, and rain probability
    """
    try:
        # Fetch 7-day forecast from OpenWeatherMap
        forecast_data = await get_weather_data(lat, lon, forecast=True)
        
        # Process forecast and calculate daily risks
        trend_data = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(forecast_data):
            risk_score, _, _ = calculate_drought_risk(
                region="General",  # Or lookup region from coordinates
                temperature=day["temp"],
                humidity=day["humidity"]
            )
            
            trend_data.append(HistoricalDataPoint(
                date=days[i],
                risk_score=float(risk_score),
                soil_moisture=100 - risk_score,
                temp=day["temp"],
                rain_probability=day.get("rain_probability", 0)
            ))
        
        return trend_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/council-alerts", response_model=List[RssFeedItem])
async def get_council_alerts():
    """
    Fetch recent water restrictions and drought alerts from regional councils.
    Uses RSS feeds parsed with feedparser library.
    
    Returns: Array of recent alerts from all NZ councils
    """
    try:
        from feedparser import parse
        from bs4 import BeautifulSoup
        
        alerts = []
        
        # Council RSS feed URLs (example)
        council_feeds = {
            "Canterbury Council": "https://example.com/rss/drought",
            "Auckland Council": "https://example.com/rss/drought",
            # ... other councils
        }
        
        for council_name, feed_url in council_feeds.items():
            try:
                feed = parse(feed_url)
                
                for entry in feed.entries[:3]:  # Get 3 most recent
                    # Clean HTML from summary
                    summary = entry.get("summary", "")
                    soup = BeautifulSoup(summary, "html.parser")
                    clean_summary = soup.get_text()
                    
                    alerts.append(RssFeedItem(
                        title=entry.title,
                        link=entry.link,
                        source=council_name,
                        published=entry.get("published", ""),
                        summary=clean_summary[:200]  # First 200 chars
                    ))
            except:
                pass  # Skip if feed unavailable
        
        return sorted(alerts, key=lambda x: x.published, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-sources", response_model=List[DataSource])
async def get_data_sources():
    """
    Get status of all data sources (NIWA, OpenWeatherMap, Council systems).
    
    Returns: Array of data sources with status and last sync time
    """
    return [
        DataSource(
            name="NIWA DataHub",
            status="active",  # or "inactive"
            last_sync="2025-11-19T10:25:00Z"
        ),
        DataSource(
            name="OpenWeatherMap",
            status="active",
            last_sync="Live"
        ),
        DataSource(
            name="Regional Councils",
            status="active",
            last_sync="2025-11-19T09:15:00Z"
        )
    ]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a message to the Gemini AI chatbot.
    
    Request: { "message": "Tell me about drought in Canterbury" }
    Response: { "response": "Canterbury is experiencing..." }
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Call Gemini AI
        response_text = await chat_with_gemini(request.message)
        
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 3. drought_risk.py - Risk Calculation

Core algorithm implementation:

```python
from typing import Tuple, Dict
import math

# Regional base risk scores
REGIONAL_BASE_RISKS = {
    "Northland": 25,
    "Auckland": 15,
    "Waikato": 55,
    "Bay of Plenty": 45,
    "Gisborne": 62,
    "Hawke's Bay": 58,
    "Taranaki": 38,
    "Manawatu-Wanganui": 42,
    "Wellington": 28,
    "Tasman": 35,
    "Nelson": 32,
    "Marlborough": 48,
    "West Coast": 20,
    "Canterbury": 65,
    "Otago": 55,
    "Southland": 35
}

# Constants
BASELINE_TEMPERATURE = 15.0  # Celsius
TARGET_HUMIDITY = 80.0       # Percentage
TEMP_WEIGHT = 2.0            # Impact multiplier for temperature
HUMIDITY_WEIGHT = 0.5        # Impact multiplier for humidity

class DroughtFactors:
    def __init__(self, rainfall_deficit: float, soil_moisture: float, temp_anomaly: float):
        self.rainfall_deficit = rainfall_deficit
        self.soil_moisture_index = soil_moisture
        self.temperature_anomaly = temp_anomaly

def calculate_drought_risk(
    region: str,
    temperature: float,
    humidity: float
) -> Tuple[int, str, DroughtFactors]:
    """
    Calculate drought risk score for a region.
    
    Args:
        region: Region name (e.g., "Canterbury")
        temperature: Current temperature in Celsius
        humidity: Current humidity percentage (0-100)
    
    Returns:
        Tuple of (risk_score, risk_level, factors)
    """
    
    # Step 1: Get regional base risk
    base_risk = REGIONAL_BASE_RISKS.get(region, 30)  # Default to 30 if unknown
    
    # Step 2: Calculate temperature anomaly
    temp_anomaly = temperature - BASELINE_TEMPERATURE
    temp_impact = temp_anomaly * TEMP_WEIGHT
    
    # Step 3: Calculate humidity deficit
    humidity_deficit = max(0, TARGET_HUMIDITY - humidity)
    humidity_impact = humidity_deficit * HUMIDITY_WEIGHT
    
    # Step 4: Calculate total risk score
    risk_score = base_risk + temp_impact + humidity_impact
    
    # Step 5: Constrain to valid range (5-99)
    risk_score = max(5, min(99, math.floor(risk_score)))
    
    # Step 6: Determine risk level
    risk_level = get_risk_level(risk_score)
    
    # Step 7: Calculate derived factors
    soil_moisture_index = 100 - risk_score
    
    factors = DroughtFactors(
        rainfall_deficit=humidity_deficit,
        soil_moisture=soil_moisture_index,
        temp_anomaly=round(temp_anomaly, 1)
    )
    
    return risk_score, risk_level, factors

def get_risk_level(risk_score: int) -> str:
    """
    Classify risk score into level (Low/Medium/High/Critical).
    
    Args:
        risk_score: Numerical risk score (0-100)
    
    Returns:
        Risk level string
    """
    if risk_score <= 25:
        return "Low"
    elif risk_score <= 50:
        return "Medium"
    elif risk_score <= 75:
        return "High"
    else:
        return "Critical"

def get_risk_color(risk_level: str) -> str:
    """Get color code for risk level."""
    colors = {
        "Low": "#22c55e",      # Green
        "Medium": "#eab308",   # Yellow
        "High": "#f97316",     # Orange
        "Critical": "#ef4444"  # Red
    }
    return colors.get(risk_level, "#94a3b8")
```

---

### 4. weather_service.py - Weather Data Integration

OpenWeatherMap integration:

```python
import httpx
import os
from typing import Dict, Optional
import asyncio

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "d7ab6944b5791f6c502a506a6049165f")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

async def get_weather_data(
    lat: float,
    lon: float,
    forecast: bool = False
) -> Dict:
    """
    Fetch weather data from OpenWeatherMap API.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        forecast: If True, fetch 7-day forecast; else current weather
    
    Returns:
        Dictionary with weather data
    """
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if forecast:
                # Get 7-day forecast
                url = f"{OPENWEATHER_BASE_URL}/forecast"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Process forecast list (typically 40 entries for 5 days, 8 per day)
                forecast_list = []
                
                for i in range(0, len(data["list"]), 8):  # Get daily forecasts
                    daily = data["list"][i]
                    forecast_list.append({
                        "temp": daily["main"]["temp"],
                        "humidity": daily["main"]["humidity"],
                        "wind_speed": daily["wind"]["speed"],
                        "pressure": daily["main"]["pressure"],
                        "weather_main": daily["weather"][0]["main"],
                        "rain_probability": daily.get("pop", 0) * 100  # PoP to percentage
                    })
                
                return forecast_list[:7]  # Return 7 days
            
            else:
                # Get current weather
                url = f"{OPENWEATHER_BASE_URL}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "pressure": data["main"]["pressure"],
                    "weather_main": data["weather"][0]["main"],
                    "visibility": data.get("visibility", 10000),
                    "clouds": data["clouds"]["all"]
                }
        
        except httpx.HTTPError as e:
            print(f"OpenWeatherMap API error: {e}")
            raise
        except Exception as e:
            print(f"Weather service error: {e}")
            raise
```

---

### 5. chatbot.py - Gemini AI Integration

Google Gemini chatbot implementation:

```python
import os
from typing import Optional
import google.generativeai as genai

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# Initialize Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

SYSTEM_INSTRUCTION = """You are the CKICAS Drought Monitor AI Assistant for New Zealand. 
Provide concise, expert advice on drought risk, rainfall, and soil moisture for NZ farmers. 
Only base your advice on general knowledge if specific real-time data is unavailable.

When discussing drought:
1. Always mention the region if specified
2. Provide actionable water management advice
3. Reference current drought risk levels (Low/Medium/High/Critical)
4. Suggest irrigation strategies based on conditions
5. Include information about regional council restrictions if known

Be friendly, professional, and focus on practical farming solutions."""

async def chat_with_gemini(user_message: str) -> str:
    """
    Send a message to Google Gemini and get a response.
    
    Args:
        user_message: User's message/question
    
    Returns:
        AI response text
    """
    
    if not GOOGLE_API_KEY:
        return "Error: Google API key not configured. Please set GOOGLE_API_KEY environment variable."
    
    try:
        # Create Generative Model
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
                top_p=0.95,
            )
        )
        
        # Generate response
        response = model.generate_content(user_message)
        
        # Extract text
        if response.text:
            return response.text
        else:
            return "I was unable to generate a response. Please try again."
    
    except genai.types.StopCandidateException:
        return "The response was blocked by safety filters. Please rephrase your question."
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"Error: Unable to process request. {str(e)}"

# Optional: For streaming responses
async def chat_with_gemini_stream(user_message: str):
    """
    Stream response from Gemini (for real-time UI updates).
    
    Yields: Chunks of response text
    """
    if not GOOGLE_API_KEY:
        yield "Error: Google API key not configured."
        return
    
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(user_message, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        yield f"Error: {str(e)}"
```

---

## Environment Variables

**.env file (backend/)**:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
OPENWEATHER_API_KEY=d7ab6944b5791f6c502a506a6049165f
NIWA_API_KEY=optional_niwa_key
```

---

## Running the Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server will start at http://localhost:9100
```

---

## API Testing

Using curl or Postman:

```bash
# Health check
curl http://localhost:9100/health

# Get drought risk for Canterbury
curl "http://localhost:9100/api/public/drought-risk?lat=-43.5&lon=171.2&region=Canterbury"

# Get forecast trend
curl "http://localhost:9100/api/public/forecast-trend?lat=-43.5&lon=171.2"

# Get council alerts
curl http://localhost:9100/api/public/council-alerts

# Get data sources status
curl http://localhost:9100/api/public/data-sources

# Chat with AI
curl -X POST http://localhost:9100/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about drought in Canterbury"}'
```

---

## Common Implementation Patterns

### 1. Error Handling
```python
try:
    # API call or calculation
    result = await some_async_operation()
except httpx.TimeoutException:
    raise HTTPException(status_code=504, detail="Request timeout")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Async/Await Pattern
```python
@app.get("/endpoint")
async def endpoint():
    # Use await for I/O operations
    result = await get_weather_data(lat, lon)
    return result
```

### 3. Data Validation with Pydantic
```python
class MyRequest(BaseModel):
    field1: str
    field2: float = 0.0  # Default value
    field3: Optional[str] = None

@app.post("/endpoint")
async def endpoint(request: MyRequest):
    # Automatic validation and type conversion
    return {"received": request.field1}
```

---

## Deployment Considerations

### Docker
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Production Settings
- Set `reload=False` in uvicorn
- Use environment variables for all secrets
- Add rate limiting middleware
- Configure logging
- Use multiple workers with gunicorn/uvicorn

---

## Performance Optimization

1. **Caching**: Implement Redis for frequently accessed data
2. **Connection pooling**: Use httpx AsyncClient with pooling
3. **Async operations**: All I/O should be async
4. **Compression**: Enable gzip compression
5. **CDN**: Cache static assets on CDN

---

## Security Best Practices

1. Never commit .env files
2. Use environment variables for all secrets
3. Validate all inputs with Pydantic
4. Implement CORS properly
5. Use HTTPS in production
6. Add rate limiting
7. Log securely (no sensitive data)

