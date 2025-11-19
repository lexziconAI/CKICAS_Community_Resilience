"""
Weather Service for CKCIAS Drought Monitor
Provides weather data functionality
"""
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from sidecar/.env
env_path = os.path.join(os.path.dirname(__file__), '..', 'sidecar', '.env')
load_dotenv(dotenv_path=env_path)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather_data(location: str):
    """
    Get weather data for a location using OpenWeather API

    Args:
        location: City name or coordinates (e.g., "London" or "London,UK")

    Returns:
        dict: Weather data with location, temperature, conditions, humidity, wind_speed

    Raises:
        Exception: If API call fails or returns invalid data
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

    params = {
        "q": location,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Use Celsius
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(OPENWEATHER_BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # Extract and format the weather data
            return {
                "location": data.get("name", location),
                "temperature": data["main"]["temp"],
                "conditions": data["weather"][0]["description"].title() if data.get("weather") else "Unknown",
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise Exception(f"Location '{location}' not found")
        elif e.response.status_code == 401:
            raise Exception("Invalid OpenWeather API key")
        else:
            raise Exception(f"OpenWeather API error: {e.response.status_code}")

    except httpx.RequestError as e:
        raise Exception(f"Network error connecting to OpenWeather API: {str(e)}")

    except (KeyError, IndexError) as e:
        raise Exception(f"Invalid response format from OpenWeather API: {str(e)}")

    except Exception as e:
        raise Exception(f"Unexpected error getting weather data: {str(e)}")
