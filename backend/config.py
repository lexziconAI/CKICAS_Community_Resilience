"""
CKCIAS Drought Monitor - Configuration
Skateboard MVP with hardcoded users and drought trigger management
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hardcoded authorized users for MVP
AUTHORIZED_USERS = [
    {
        "id": 1,
        "email": "regan@axiomintelligence.co.nz",
        "name": "Regan",
        "region": "Auckland",
        "organization": "Axiom Intelligence"
    },
    {
        "id": 2,
        "email": "tim.house@fonterra.com",
        "name": "Tim House",
        "region": "Taranaki",
        "organization": "Fonterra"
    }
]

# Available indicators for drought monitoring
AVAILABLE_INDICATORS = {
    "temp": {
        "label": "Temperature",
        "unit": "°C",
        "type": "number"
    },
    "rainfall": {
        "label": "Rainfall",
        "unit": "mm",
        "type": "number"
    },
    "humidity": {
        "label": "Humidity",
        "unit": "%",
        "type": "number"
    },
    "wind_speed": {
        "label": "Wind Speed",
        "unit": "km/h",
        "type": "number"
    }
}

# Combination rules for triggers
COMBINATION_RULES = ["any_1", "any_2", "any_3", "all"]

# SendGrid API configuration (for email notifications)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# Database configuration
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "ckcias.db"
)

# FastAPI configuration
API_PORT = 9100
API_HOST = "0.0.0.0"

# CORS origins
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080"
]
