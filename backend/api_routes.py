"""
API Routes for CKCIAS Drought Monitor
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime, timedelta

from weather_service import get_weather_data
from drought_risk import calculate_drought_risk
from chatbot import chat_with_gemini

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    conditions: str
    humidity: float
    wind_speed: float

class DroughtRiskResponse(BaseModel):
    risk_level: str
    risk_score: float
    factors: dict

# Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI assistant about drought conditions"""
    try:
        print(f"\n🔵 BACKEND RECEIVED MESSAGE ({len(request.message)} chars):")
        print(f"First 300 chars: {request.message[:300]}")
        response_text = await chat_with_gemini(request.message)
        print(f"✅ BACKEND SENDING RESPONSE ({len(response_text)} chars):")
        print(f"First 200 chars: {response_text[:200]}\n")
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# Weather endpoint
@router.get("/weather", response_model=WeatherResponse)
async def get_weather(location: str = "Christchurch"):
    """Get current weather data for a location"""
    try:
        weather_data = await get_weather_data(location)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")

# Drought risk endpoint
@router.get("/drought-risk", response_model=DroughtRiskResponse)
async def get_drought_risk(location: str = "Canterbury"):
    """Calculate drought risk for a region"""
    try:
        risk_data = await calculate_drought_risk(location)
        return risk_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drought risk calculation error: {str(e)}")

# Test endpoint
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "CKCIAS API is operational",
        "endpoints": ["/api/chat", "/api/weather", "/api/drought-risk"]
    }

# Public drought risk endpoint (with lat/lon and region params)
@router.get("/public/drought-risk")
async def get_public_drought_risk(lat: float, lon: float, region: str):
    """Calculate drought risk for a specific region with coordinates"""
    try:
        risk_data = await calculate_drought_risk(region)
        return risk_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drought risk calculation error: {str(e)}")

# Data sources status endpoint
@router.get("/public/data-sources")
async def get_data_sources():
    """Get status of all data sources"""
    return [
        {"name": "OpenWeatherMap", "status": "active", "last_sync": "Real-time"},
        {"name": "NIWA DataHub", "status": "inactive", "last_sync": "Not configured"},
        {"name": "Regional Councils", "status": "inactive", "last_sync": "Not configured"}
    ]

# Council alerts endpoint
@router.get("/public/council-alerts")
async def get_council_alerts():
    """Get council water restriction alerts via RSS/Scraping (No Mocks)"""
    # In a real production system, this would scrape specific council pages
    # For now, we will return an empty list rather than fake data
    # to strictly adhere to the "No Mock Data" policy.
    # Future: Implement specific scrapers for each council.
    return []

# News headlines endpoint
@router.get("/public/news-headlines")
async def get_news_headlines():
    """Get farming and weather news headlines from RSS feeds"""
    import feedparser
    from datetime import datetime, timedelta

    headlines = []

    # RSS Feed sources
    feeds = [
        {
            "url": "https://www.rnz.co.nz/rss/rural.xml",
            "source": "RNZ Rural"
        },
        {
            "url": "https://feeds.feedburner.com/RuralNews",
            "source": "Rural News"
        }
    ]

    for feed_config in feeds:
        try:
            feed = feedparser.parse(feed_config["url"])
            # Get first 5 entries from each feed
            for entry in feed.entries[:5]:
                headlines.append({
                    "title": entry.title,
                    "link": entry.get("link", ""),
                    "source": feed_config["source"],
                    "published": entry.get("published", datetime.now().isoformat())
                })
        except Exception as e:
            print(f"Error fetching {feed_config['source']}: {str(e)}")
            continue

    # If no RSS feeds work, return error (No Mocks)
    if not headlines:
        raise HTTPException(status_code=502, detail="News Feeds Unavailable")

    return headlines

# Forecast trend endpoint (Real Data via OpenWeatherMap)
@router.get("/public/forecast-trend")
async def get_forecast_trend(lat: float, lon: float):
    """Get 5-day forecast trend for region using OpenWeatherMap"""
    import httpx
    import os
    from datetime import datetime

    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Server Configuration Error: Missing Weather API Key")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Using the 5-day/3-hour forecast API which is free and standard
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Process 3-hour intervals into daily summaries
            daily_data = {}
            for item in data.get('list', []):
                dt = datetime.fromtimestamp(item['dt'])
                date_str = dt.strftime('%a') # Mon, Tue, etc.
                
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'temps': [],
                        'rain_probs': [],
                        'humidities': []
                    }
                
                daily_data[date_str]['temps'].append(item['main']['temp'])
                daily_data[date_str]['humidities'].append(item['main']['humidity'])
                # Pop is probability of precipitation (0-1)
                daily_data[date_str]['rain_probs'].append(item.get('pop', 0) * 100)

            # Format for frontend
            forecast_trend = []
            # Limit to next 5 days to ensure data quality
            for day, metrics in list(daily_data.items())[:5]:
                avg_temp = sum(metrics['temps']) / len(metrics['temps'])
                avg_humidity = sum(metrics['humidities']) / len(metrics['humidities'])
                max_rain_prob = max(metrics['rain_probs']) if metrics['rain_probs'] else 0
                
                # Calculate a dynamic risk score based on real metrics
                # High temp + Low humidity = High Risk
                # 15C baseline. 80% humidity baseline.
                temp_factor = max(0, avg_temp - 15) * 2
                humidity_factor = max(0, 80 - avg_humidity) * 0.5
                risk_score = min(99, max(5, 30 + temp_factor + humidity_factor))

                forecast_trend.append({
                    "date": day,
                    "risk_score": round(risk_score, 1),
                    "soil_moisture": round(100 - risk_score, 1), # Inverse proxy for soil moisture
                    "temp": round(avg_temp, 1),
                    "rain_probability": round(max_rain_prob, 0)
                })
            
            return forecast_trend

    except Exception as e:
        # STRICT NO MOCK POLICY: Return error if real data fails
        print(f"Forecast API Error: {str(e)}")
        raise HTTPException(status_code=502, detail="Weather Data Unavailable")

# Cache for weather narrative (regenerate every 30 minutes)
_narrative_cache = {"narrative": None, "timestamp": None}

@router.get("/public/weather-narrative")
async def get_weather_narrative():
    """
    Generate a philosophical, multi-layered narrative about NZ weather conditions.
    Embodies Gregory David Roberts' lyrical style and quantum storytelling principles.
    Regenerates every 30 minutes.
    """
    import feedparser
    
    # Check cache (30 min TTL)
    if _narrative_cache["narrative"] and _narrative_cache["timestamp"]:
        age = datetime.now() - _narrative_cache["timestamp"]
        if age < timedelta(minutes=30):
            return {"narrative": _narrative_cache["narrative"], "generated_at": _narrative_cache["timestamp"].isoformat()}
    
    # Gather contextual data
    try:
        # Get news headlines
        headlines = []
        feeds = [
            {"url": "https://www.rnz.co.nz/rss/rural.xml", "source": "RNZ"},
            {"url": "https://feeds.feedburner.com/RuralNews", "source": "Rural"}
        ]
        for feed_config in feeds:
            try:
                feed = feedparser.parse(feed_config["url"])
                for entry in feed.entries[:3]:
                    headlines.append(entry.title)
            except:
                pass
        
        # Get council alerts (water status across regions)
        alerts = await get_council_alerts()
        
        # Build the prompt - embodying Roberts' style and quantum storytelling
        context = f"""Current Headlines: {'; '.join(headlines[:5]) if headlines else 'Weather patterns shifting across regions'}

Regional Water Status: {', '.join([f"{a['region']} ({a['severity']})" for a in alerts[:4]])}"""
        
        prompt = f"""You are a storyteller weaving the living narrative of Aotearoa New Zealand's relationship with water and land.

Write a single, flowing paragraph (2-3 sentences) that captures this moment in time. Write as if you're Gregory David Roberts observing the intricate dance between human communities and natural systems - poetic yet grounded, philosophical yet practical.

Context:
{context}

Channel these principles without stating them explicitly:
- See the farm, the region, the nation, and the ecosystem as nested cycles of adaptation
- Multiple stories happening simultaneously: the farmer's daily choice, the regional council's watch, the aquifer's slow response
- Every moment contains seeds of both vulnerability and resilience

Write with: Rich imagery. Deep humanity. A touch of wonder. Practical wisdom embedded in beauty. Focus on drought prevention and water wisdom, but see the whole living system.

Begin directly with the narrative - no preamble, no meta-commentary. Just the story."""
        
        # Generate narrative
        narrative = await chat_with_gemini(prompt)

        # Clean up (remove any meta text, markdown, and extra formatting)
        narrative = narrative.strip().replace('"', '').replace('*', '').replace('#', '').replace('\n', ' ').strip()
        # Remove multiple spaces
        while '  ' in narrative:
            narrative = narrative.replace('  ', ' ')
        
        # Cache it
        _narrative_cache["narrative"] = narrative
        _narrative_cache["timestamp"] = datetime.now()
        
        return {"narrative": narrative, "generated_at": datetime.now().isoformat()}
        
    except Exception as e:
        # No Fallback - Return Error
        print(f"Narrative Generation Error: {str(e)}")
        raise HTTPException(status_code=502, detail="Narrative Generation Unavailable")

# TRC Hilltop Server Integration
@router.get("/public/hilltop/sites")
async def get_hilltop_sites():
    """Get monitoring sites from TRC Hilltop Server with coordinates"""
    import httpx
    import xml.etree.ElementTree as ET

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://extranet.trc.govt.nz/getdata/merged.hts",
                params={
                    "Service": "Hilltop",
                    "Request": "SiteList",
                    "Location": "LatLong"
                }
            )
            response.raise_for_status()

            # Parse XML response with basic validation
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as parse_err:
                raise HTTPException(status_code=502, detail="Invalid XML from data source")

            sites = []

            for site in root.findall('Site'):
                site_name = site.get('Name')
                lat_elem = site.find('Latitude')
                lon_elem = site.find('Longitude')

                if lat_elem is not None and lon_elem is not None:
                    sites.append({
                        "name": site_name,
                        "latitude": float(lat_elem.text),
                        "longitude": float(lon_elem.text),
                        "region": "Taranaki"
                    })

            return {"sites": sites, "count": len(sites)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail="External data source unavailable")

@router.get("/public/hilltop/measurements")
async def get_hilltop_measurements(site: str):
    """Get available measurements for a specific site"""
    import httpx
    import xml.etree.ElementTree as ET

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://extranet.trc.govt.nz/getdata/merged.hts",
                params={
                    "Service": "Hilltop",
                    "Request": "MeasurementList",
                    "Site": site
                }
            )
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            measurements = []

            for datasource in root.findall('.//DataSource'):
                ds_name = datasource.get('Name')
                for item in datasource.findall('.//ItemInfo'):
                    meas_name = item.find('ItemName')
                    units = item.find('Units')

                    if meas_name is not None:
                        measurements.append({
                            "name": meas_name.text,
                            "units": units.text if units is not None else "",
                            "datasource": ds_name
                        })

            return {"site": site, "measurements": measurements}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail="External data source unavailable")

@router.get("/public/hilltop/data")
async def get_hilltop_data(site: str, measurement: str, days: int = 7):
    """Get actual data for a site/measurement combination"""
    import httpx
    import xml.etree.ElementTree as ET

    # Input validation - prevent DOS
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                "https://extranet.trc.govt.nz/getdata/merged.hts",
                params={
                    "Service": "Hilltop",
                    "Request": "GetData",
                    "Site": site,
                    "Measurement": measurement,
                    "TimeInterval": f"P{days}D"
                }
            )
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            data_points = []

            for element in root.findall('.//Data/E'):
                time_elem = element.find('T')
                value_elem = element.find('I1')

                if time_elem is not None and value_elem is not None:
                    data_points.append({
                        "timestamp": time_elem.text,
                        "value": float(value_elem.text)
                    })

            # Get units
            units = ""
            units_elem = root.find('.//Units')
            if units_elem is not None:
                units = units_elem.text

            return {
                "site": site,
                "measurement": measurement,
                "units": units,
                "data": data_points,
                "count": len(data_points)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail="External data source unavailable")
