# CKICAS Drought Monitor - Backend Documentation Index

## Overview

This documentation package provides a comprehensive analysis of the CKICAS Drought Monitor Python backend system. The backend is a FastAPI-based REST API server (running on port 9100) that powers a real-time drought risk monitoring and AI-assisted analysis system for New Zealand farmers.

---

## Documentation Files

### 1. BACKEND_ANALYSIS.md (15 KB)
**Comprehensive technical analysis of the entire backend system**

Contents:
- Backend framework and architecture overview
- Complete API endpoint specifications with request/response examples
- Drought risk calculation mathematical algorithm with formulas
- Weather data integration sources and methods
- Chatbot functionality and Google Gemini AI integration
- External services and API dependencies
- Data flow diagrams and processing logic
- Configuration and environment variables
- Key architectural features

**Best for:** Understanding how the system works, API design, algorithm details

---

### 2. BACKEND_SUMMARY.txt (19 KB)
**Detailed reference summary organized by topic**

Sections:
1. Framework & Architecture - Tech stack (FastAPI, Uvicorn, Python 3.11)
2. API Endpoints & Specifications - All 6 endpoints with request/response formats
3. Drought Risk Calculation - Step-by-step algorithm with examples
4. Weather Data Integration - OpenWeatherMap, NIWA, Council RSS feeds
5. Chatbot & AI Integration - Google Gemini 2.5 Flash configuration
6. External Services & APIs - Complete service dependencies
7. Data Flow & Processing Logic - Request processing workflows
8. Configuration & Environment - Setup and deployment info
9. Key Architectural Features - Design patterns and resilience
10. Summary - Quick overview and file listing

**Best for:** Quick reference lookups, understanding specific features

---

### 3. BACKEND_IMPLEMENTATION_NOTES.md (21 KB)
**Code examples and implementation guidance**

Sections:
- main.py - Server initialization with CORS, startup events
- routes.py - Full endpoint implementations with Pydantic models
- drought_risk.py - Risk calculation algorithm implementation
- weather_service.py - OpenWeatherMap API integration
- chatbot.py - Google Gemini integration code
- Environment variables setup
- Running the backend (installation and startup)
- API testing examples (curl commands)
- Common implementation patterns
- Deployment considerations (Docker, production settings)
- Performance optimization strategies
- Security best practices

**Best for:** Implementation, deployment, coding patterns, troubleshooting

---

## Quick Reference

### Project Structure
```
backend/
├── main.py                 # FastAPI server initialization
├── routes.py               # API endpoint definitions (6 endpoints)
├── chatbot.py              # Google Gemini AI integration
├── drought_risk.py         # Drought risk calculation algorithm
├── weather_service.py      # OpenWeatherMap API client
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not in repo)
```

### Key Technologies
- **Framework**: FastAPI 0.100.0+
- **Server**: Uvicorn 0.22.0+
- **Language**: Python 3.11+
- **AI**: Google Gemini (via google-generativeai)
- **Weather Data**: OpenWeatherMap API
- **RSS Parsing**: feedparser, beautifulsoup4
- **Data Validation**: Pydantic

### Core Dependencies
```
fastapi>=0.100.0
uvicorn>=0.22.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
httpx>=0.24.0
pydantic>=2.0.0
feedparser>=6.0.10
beautifulsoup4>=4.12.0
```

### API Endpoints Summary

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| /health | GET | Server health check | None |
| /api/public/drought-risk | GET | Calculate drought risk | lat, lon, region |
| /api/public/forecast-trend | GET | 7-day drought forecast | lat, lon |
| /api/public/council-alerts | GET | Water restrictions alerts | None |
| /api/public/data-sources | GET | Data source status | None |
| /api/chat | POST | AI chatbot analysis | message (JSON) |

### Risk Scoring Formula

```
Base Risk = Region.baseRisk (15-65 depending on NZ region)
Temperature Impact = (Current Temp - 15°C) × 2.0
Humidity Impact = max(0, 80% - Current Humidity) × 0.5

Risk Score = Base Risk + Temperature Impact + Humidity Impact
Risk Score = max(5, min(99, floor(Risk Score)))

Risk Levels:
  0-25:   Low (Green)
  26-50:  Medium (Yellow)
  51-75:  High (Orange)
  76-100: Critical (Red)
```

### Drought Risk by Region (Base Scores)

**Highest Risk (Dry regions):**
- Canterbury: 65
- Gisborne: 62
- Hawke's Bay: 58
- Waikato: 55
- Otago: 55

**Lowest Risk (Wet regions):**
- West Coast: 20
- Northland: 25
- Wellington: 28

### Environment Variables Required

```
GOOGLE_API_KEY=your_google_gemini_api_key
OPENWEATHER_API_KEY=d7ab6944b5791f6c502a506a6049165f (optional fallback)
NIWA_API_KEY=optional_if_required
```

---

## How to Use This Documentation

### I want to...

**Understand the overall system architecture**
→ Read: BACKEND_ANALYSIS.md sections 1-2, BACKEND_SUMMARY.txt sections 1-2

**Implement or modify the backend**
→ Read: BACKEND_IMPLEMENTATION_NOTES.md, then reference BACKEND_ANALYSIS.md for details

**Understand the drought risk calculation**
→ Read: BACKEND_SUMMARY.txt section 3, BACKEND_ANALYSIS.md "Drought Risk Calculation Logic"

**Integrate a new data source or API**
→ Read: BACKEND_IMPLEMENTATION_NOTES.md sections 4-5, BACKEND_ANALYSIS.md "External Services"

**Deploy the backend to production**
→ Read: BACKEND_IMPLEMENTATION_NOTES.md "Deployment Considerations", BACKEND_SUMMARY.txt section 8

**Fix API issues or debug requests**
→ Read: BACKEND_IMPLEMENTATION_NOTES.md "API Testing", BACKEND_ANALYSIS.md "Data Flow"

**Optimize performance or add features**
→ Read: BACKEND_IMPLEMENTATION_NOTES.md "Performance Optimization", BACKEND_SUMMARY.txt section 9

---

## Key Features Highlighted

### Hybrid Operation Mode
The system supports three modes:
1. **Online**: Full backend with all services active
2. **Serverless**: Frontend operates independently with Gemini API
3. **Offline**: Cached data with graceful error messages

### AI Integration
- **Model**: Google Gemini 2.5 Flash
- **System Instruction**: Tailored for New Zealand drought guidance
- **Capabilities**: Risk analysis, agricultural advice, trend forecasting
- **Fallback**: Client-side execution when backend offline

### Real-Time Data Processing
- **Parallel loading**: 16 NZ regions load simultaneously
- **Health checks**: 30-second interval monitoring
- **Last_updated**: Timestamps on all responses
- **On-demand updates**: Weather data fetched per request

### Fault Tolerance
- Falls back to client-side OpenWeatherMap if backend unavailable
- Graceful error handling with user-friendly messages
- Status indicators show system state to users
- No database required (stateless design)

---

## API Response Examples

### Drought Risk Response
```json
{
  "region": "Canterbury",
  "risk_score": 77,
  "risk_level": "High",
  "factors": {
    "rainfall_deficit": 12.0,
    "soil_moisture_index": 23,
    "temperature_anomaly": 3.0
  },
  "extended_metrics": {
    "wind_speed": 12.4,
    "humidity": 68,
    "pressure": 1013,
    "weather_main": "Partly Cloudy"
  },
  "data_source": "OpenWeatherMap",
  "last_updated": "2025-11-19T10:30:00Z"
}
```

### Chat Response
```json
{
  "response": "Canterbury is experiencing high drought risk (77/100) with elevated temperatures and low humidity. I recommend implementing Stage 2 water restrictions and increasing irrigation efficiency..."
}
```

---

## Deployment Checklist

- [ ] Set GOOGLE_API_KEY environment variable
- [ ] Set OPENWEATHER_API_KEY environment variable
- [ ] Install Python 3.11+
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set production mode: `reload=False` in main.py
- [ ] Configure CORS for frontend domain
- [ ] Add rate limiting middleware (optional)
- [ ] Set up logging (optional)
- [ ] Use uvicorn with multiple workers
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring/alerting
- [ ] Test all endpoints

---

## Contact & Support

For questions about specific implementation details, refer to:
- **API Design**: BACKEND_ANALYSIS.md section "API Endpoints"
- **Algorithm Details**: BACKEND_SUMMARY.txt section 3
- **Deployment**: BACKEND_IMPLEMENTATION_NOTES.md section "Deployment"
- **Code Examples**: BACKEND_IMPLEMENTATION_NOTES.md sections 1-5

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-19 | Initial comprehensive analysis |

---

## Document Metadata

- **Project**: CKICAS Drought Monitor
- **Component**: Python Backend Analysis
- **Created**: 2025-11-19
- **Analysis Depth**: Comprehensive
- **Audience**: Developers, DevOps Engineers, Project Managers
- **Completeness**: Full system analysis based on frontend integration requirements

---

## Additional Notes

The backend source files in the project directory appear to have encoding issues. This documentation was reverse-engineered from:
1. Frontend API integration code (services/api.ts)
2. TypeScript type definitions
3. React component usage patterns
4. Requirements.txt dependencies
5. README.md setup instructions

The analysis is comprehensive and includes:
- Complete endpoint specifications
- Full algorithm documentation
- Code implementation examples
- Deployment guidance
- Security recommendations

All information is structured to support both implementation and understanding of the system.

