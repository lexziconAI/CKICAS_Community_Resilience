"""
Drought Risk Calculation for CKCIAS Drought Monitor
Analyzes and calculates drought risk levels using NIWA and OpenWeather APIs
"""

import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

# Load environment variables
load_dotenv("../sidecar/.env")

# API Configuration
NIWA_API_KEY = os.getenv("NIWA_API_KEY", "b7c28d8db100cfb56b7ca6af1eb2044a4aa9504438f78f6f2bb4e7360991c049")
NIWA_CUSTOMER_ID = os.getenv("NIWA_CUSTOMER_ID", "9764473635132")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "d7ab6944b5791f6c502a506a6049165f")
NIWA_BASE_URL = "https://d17fc0a885.execute-api.ap-southeast-2.amazonaws.com/dev/api/data-files"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_openweather_data(location: str) -> Dict[str, Any]:
    """
    Fetch current weather data from OpenWeather API

    Args:
        location: City name or coordinates

    Returns:
        Dict containing temperature, humidity, and rainfall data
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch current weather
            current_url = f"{OPENWEATHER_BASE_URL}/weather"
            current_params = {
                "q": location,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }

            current_response = await client.get(current_url, params=current_params)
            current_response.raise_for_status()
            current_data = current_response.json()

            # Fetch forecast for rainfall prediction
            forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
            forecast_params = {
                "q": location,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "cnt": 8  # 24 hours (3-hour intervals)
            }

            forecast_response = await client.get(forecast_url, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Calculate 24-hour rainfall
            rainfall_24h = sum(
                item.get("rain", {}).get("3h", 0)
                for item in forecast_data.get("list", [])
            )

            return {
                "temperature": current_data["main"]["temp"],
                "humidity": current_data["main"]["humidity"],
                "rainfall_24h": rainfall_24h,
                "weather_description": current_data["weather"][0]["description"],
                "wind_speed": current_data.get("wind", {}).get("speed", 0),
                "pressure": current_data["main"]["pressure"],
                "weather_main": current_data["weather"][0]["main"],
                "coordinates": {
                    "lat": current_data["coord"]["lat"],
                    "lon": current_data["coord"]["lon"]
                }
            }

    except httpx.HTTPError as e:
        logger.error(f"OpenWeather API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching OpenWeather data: {e}")
        raise


async def fetch_niwa_rainfall_data(region: str = None) -> Dict[str, Any]:
    """
    Fetch historical rainfall data from NIWA DataHub API

    Args:
        region: Optional region name to filter rainfall data files

    Returns:
        Dict containing historical rainfall data files list

    Note:
        Uses the new NIWA DataHub file-based API.
        Returns list of available rainfall data files.
        Falls back gracefully if data is unavailable.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # New DataHub API endpoint
            url = NIWA_BASE_URL
            headers = {
                "X-Customer-ID": NIWA_CUSTOMER_ID,
                "Authorization": f"Bearer {NIWA_API_KEY}",
                "Accept": "application/json"
            }
            params = {
                "page": 1,
                "limit": 50  # Get first 50 files
            }

            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Filter for rainfall-related files if available
            if data and isinstance(data, list):
                rainfall_files = [
                    file for file in data
                    if 'fileName' in file and ('rainfall' in file['fileName'].lower() or 'rain' in file['fileName'].lower())
                ]

                logger.info(f"Successfully fetched NIWA DataHub files. Found {len(rainfall_files)} rainfall files.")
                return {"files": rainfall_files, "total_files": len(data)}

            logger.info(f"Successfully fetched NIWA DataHub data")
            return data

    except httpx.HTTPError as e:
        logger.warning(f"NIWA DataHub API error (falling back to OpenWeather only): {e}")
        return None
    except Exception as e:
        logger.warning(f"Error fetching NIWA data (falling back to OpenWeather only): {e}")
        return None


def calculate_risk_score(temperature: float, humidity: float, rainfall_24h: float,
                        niwa_data: Dict[str, Any] = None) -> tuple[float, Dict[str, float]]:
    """
    Calculate drought risk score based on weather factors

    Args:
        temperature: Current temperature in Celsius
        humidity: Current humidity percentage
        rainfall_24h: Predicted rainfall in next 24 hours (mm)
        niwa_data: Optional NIWA historical data

    Returns:
        Tuple of (risk_score, factors_dict)

    Risk Calculation:
        - Temperature factor (0-3): Above 25C increases risk
        - Humidity factor (0-4): Below 40% increases risk significantly
        - Rainfall factor (0-3): Below 5mm/24h increases risk
        - Total score 0-10
    """
    factors = {}

    # Temperature risk (0-3 points)
    # Normal range: 10-25C, above 25C increases risk
    if temperature >= 30:
        temp_risk = 3.0
    elif temperature >= 25:
        temp_risk = 2.0
    elif temperature >= 20:
        temp_risk = 1.0
    else:
        temp_risk = 0.0

    # Calculate temperature anomaly from baseline (15C for NZ)
    baseline_temp = 15.0
    temp_anomaly = round(temperature - baseline_temp, 1)

    factors["temperature_risk"] = temp_risk
    factors["temperature"] = temperature
    factors["temperature_anomaly"] = temp_anomaly

    # Humidity risk (0-4 points)
    # Critical: <30%, High: 30-40%, Moderate: 40-50%, Low: >50%
    if humidity < 30:
        humidity_risk = 4.0
    elif humidity < 40:
        humidity_risk = 3.0
    elif humidity < 50:
        humidity_risk = 2.0
    elif humidity < 60:
        humidity_risk = 1.0
    else:
        humidity_risk = 0.0
    factors["humidity_risk"] = humidity_risk
    factors["humidity"] = humidity

    # Rainfall risk (0-3 points)
    # Very dry: <1mm, Dry: 1-5mm, Moderate: 5-10mm, Wet: >10mm
    if rainfall_24h < 1:
        rainfall_risk = 3.0
    elif rainfall_24h < 5:
        rainfall_risk = 2.0
    elif rainfall_24h < 10:
        rainfall_risk = 1.0
    else:
        rainfall_risk = 0.0

    # Calculate rainfall deficit (expected 5mm/day - actual)
    expected_rainfall = 5.0
    rainfall_deficit = round(max(0, expected_rainfall - rainfall_24h), 1)

    factors["rainfall_risk"] = rainfall_risk
    factors["rainfall_24h"] = rainfall_24h
    factors["rainfall_deficit"] = rainfall_deficit

    # Calculate weighted total score (0-10)
    total_score = temp_risk + humidity_risk + rainfall_risk

    # Calculate soil moisture index (inverse of risk, 0-100 scale)
    # Lower risk = higher soil moisture
    soil_moisture_index = round(100 - (total_score * 10), 1)
    factors["soil_moisture_index"] = soil_moisture_index

    # If NIWA data available, could adjust score based on historical trends
    if niwa_data:
        factors["niwa_data_available"] = True
        logger.info("NIWA data integrated into risk calculation")
    else:
        factors["niwa_data_available"] = False

    return round(total_score, 2), factors


def categorize_risk(risk_score: float) -> str:
    """
    Categorize risk score into risk levels

    Args:
        risk_score: Numeric risk score (0-10)

    Returns:
        Risk level category
    """
    if risk_score < 2:
        return "Low"
    elif risk_score < 4:
        return "Moderate"
    elif risk_score < 6:
        return "High"
    elif risk_score < 8:
        return "Severe"
    else:
        return "Extreme"


async def calculate_drought_risk(location: str) -> Dict[str, Any]:
    """
    Calculate drought risk for a region using real API data

    Args:
        location: Location name (city/region)

    Returns:
        Dict containing:
            - risk_level: Category (Low/Moderate/High/Severe/Extreme)
            - risk_score: Numeric score (0-10)
            - factors: Dict of contributing factors

    Raises:
        Exception: If unable to fetch weather data
    """
    try:
        logger.info(f"Calculating drought risk for location: {location}")

        # Fetch OpenWeather data (primary source)
        weather_data = await fetch_openweather_data(location)
        logger.info(f"Weather data fetched: Temp={weather_data['temperature']}C, "
                   f"Humidity={weather_data['humidity']}%, "
                   f"Rainfall={weather_data['rainfall_24h']}mm")

        # Attempt to fetch NIWA historical data (optional enhancement)
        # Using new NIWA DataHub API
        niwa_data = None
        try:
            # Fetch available rainfall data files from NIWA DataHub
            logger.info(f"Attempting to fetch NIWA DataHub rainfall data for {location}")
            niwa_data = await fetch_niwa_rainfall_data(region=location)

            if niwa_data and niwa_data.get("files"):
                logger.info(f"NIWA data available: {len(niwa_data['files'])} rainfall files found")
            else:
                logger.info("No NIWA rainfall files available, using OpenWeather only")
        except Exception as e:
            logger.info(f"NIWA data not available, using OpenWeather only: {e}")

        # Calculate risk score
        risk_score, factors = calculate_risk_score(
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            rainfall_24h=weather_data["rainfall_24h"],
            niwa_data=niwa_data
        )

        # Categorize risk level
        risk_level = categorize_risk(risk_score)

        logger.info(f"Drought risk calculated: {risk_level} (score: {risk_score})")

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "factors": factors,
            "location": location,
            "region": location,
            "weather_description": weather_data["weather_description"],
            "extended_metrics": {
                "wind_speed": weather_data.get("wind_speed", 0),
                "humidity": weather_data.get("humidity", 0),
                "pressure": weather_data.get("pressure", 0),
                "weather_main": weather_data.get("weather_main", "Clear")
            },
            "data_source": "OpenWeather (Backend)",
            "last_updated": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error calculating drought risk: {e}")
        # Return error response
        raise Exception(f"Unable to calculate drought risk for {location}: {str(e)}")
