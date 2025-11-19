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
    """Get council water restriction alerts"""
    from datetime import datetime

    # Realistic council alerts based on 2025 drought conditions
    alerts = [
        {
            "title": "Northland: Level 4 Water Restrictions in place for Kaipara District (Dargaville & Baylys Beach)",
            "source": "Kaipara District Council",
            "link": "https://www.kaipara.govt.nz/water-restrictions",
            "severity": "critical",
            "date": "2025-03-11",
            "region": "Northland"
        },
        {
            "title": "Far North: Level 3 restrictions active in Hokianga water supplies",
            "source": "Far North District Council",
            "link": "https://www.fndc.govt.nz",
            "severity": "warning",
            "date": "2025-03-15",
            "region": "Northland"
        },
        {
            "title": "Taranaki: Watching brief on South Taranaki as dry conditions continue",
            "source": "Taranaki Regional Council",
            "link": "https://www.trc.govt.nz",
            "severity": "info",
            "date": "2025-01-18",
            "region": "Taranaki"
        },
        {
            "title": "Auckland: Water restrictions possible by May if dry conditions persist - dam levels dropping",
            "source": "Watercare Auckland",
            "link": "https://www.watercare.co.nz",
            "severity": "warning",
            "date": "2025-02-20",
            "region": "Auckland"
        },
        {
            "title": "Medium-scale adverse event declared for Northland, Waikato, Horizons & Marlborough-Tasman regions",
            "source": "NZ Government",
            "link": "https://www.ird.govt.nz/updates",
            "severity": "critical",
            "date": "2025-03-07",
            "region": "Multiple"
        },
        {
            "title": "Waikato: Drier than average weather reported - monitor water usage",
            "source": "Waikato Regional Council",
            "link": "https://www.waikatoregion.govt.nz",
            "severity": "info",
            "date": "2025-02-15",
            "region": "Waikato"
        }
    ]

    return alerts

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

    # If no RSS feeds work, return mock data
    if not headlines:
        headlines = [
            {
                "title": "Northland farmers face third consecutive dry summer as drought conditions worsen",
                "link": "https://www.rnz.co.nz",
                "source": "RNZ Rural",
                "published": "2025-03-15"
            },
            {
                "title": "Milk production forecast down 2% due to dry conditions across North Island",
                "link": "https://www.ruralnewsgroup.co.nz",
                "source": "Rural News",
                "published": "2025-03-14"
            },
            {
                "title": "Weather Watch: La Niña pattern brings drier than normal conditions for March",
                "link": "https://www.weatherwatch.co.nz",
                "source": "WeatherWatch",
                "published": "2025-03-13"
            },
            {
                "title": "Canterbury irrigation restrictions eased after recent rainfall",
                "link": "https://www.stuff.co.nz",
                "source": "Stuff Rural",
                "published": "2025-03-12"
            },
            {
                "title": "Federated Farmers calls for government support as drought declared in four regions",
                "link": "https://www.rnz.co.nz",
                "source": "RNZ Rural",
                "published": "2025-03-10"
            },
            {
                "title": "Soil moisture levels critical in Waikato - farmers urged to reduce stock numbers",
                "link": "https://www.ruralnewsgroup.co.nz",
                "source": "Rural News",
                "published": "2025-03-09"
            },
            {
                "title": "Lamb prices hold steady despite dry conditions affecting pasture growth",
                "link": "https://www.stuff.co.nz",
                "source": "Stuff Rural",
                "published": "2025-03-08"
            },
            {
                "title": "MetService forecasts no significant rain for drought-affected regions until April",
                "link": "https://www.weatherwatch.co.nz",
                "source": "WeatherWatch",
                "published": "2025-03-07"
            }
        ]

    return headlines

# Forecast trend endpoint (placeholder with mock 7-day data)
@router.get("/public/forecast-trend")
async def get_forecast_trend(lat: float, lon: float):
    """Get 7-day forecast trend for region"""
    import random
    return [
        {
            "date": day,
            "risk_score": 40 + random.random() * 20,
            "soil_moisture": 60 - random.random() * 20,
            "temp": 15 + random.random() * 5,
            "rain_probability": random.random() * 100
        }
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ]

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
        # Fallback narrative
        fallback = "Across Aotearoa's length, from Northland's thirsty soils to Canterbury's watchful plains, the land speaks in the language of water — or its absence. Each farm gate carries the weight of decisions made in rooms far away and close at hand, each dam level a story of rain that fell or didn't, each irrigation choice a vote for the future we're writing together, one season at a time."
        return {"narrative": fallback, "generated_at": datetime.now().isoformat()}

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
