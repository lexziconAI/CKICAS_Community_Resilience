# CKCIAS Copilot Instructions

## Architecture snapshot
- React + Vite frontend (root `App.tsx`) renders the map/AI dashboard and uses hooks in `components/` for UI.
- FastAPI backend (`backend/main.py`, `routes.py`) exposes `/health`, `/api/public/*`, and `/api/chat` with algorithms defined in `drought_risk.py` and `weather_service.py`; see `BACKEND_SUMMARY.txt` for parameter contracts.
- `sidecar/` is an optional multi-provider LLM control-plane (FastAPI + WebSocket dashboard) that can replace/augment the default chat by running `python sidecar/main_app.py`.

## Frontend conventions
- All network calls flow through `services/api.ts`; reuse `safeFetch` so offline/serverless fallbacks (OpenWeather + client-side Gemini) keep working.
- Region metadata and color scales live in `constants.ts`; update `NZ_REGIONS`/`RISK_COLORS` instead of scattering values inside components.
- Types are centralized in `types.ts`; extend these before touching component state so `App.tsx`, `DroughtMap.tsx`, `HistoricalChart.tsx`, etc. stay in sync with backend JSON.
- Leaflet CSS is injected via `index.html`; new map layers should go through `DroughtMap` to keep the invalidateSize workaround in `MapController`.
- `ChatInterface.tsx` auto-sends a prompt when `selectedRegion` changes—avoid triggering duplicate `handleSend` calls when wiring new UI inputs.

## Backend expectations
- Spin up the API with `cd backend && python -m venv venv && venv\Scripts\activate && python main.py` (or `uvicorn main:app --reload`); keep endpoints congruent with the shapes documented in `BACKEND_SUMMARY.txt`.
- The drought risk score is `baseRisk + tempAnomaly*2 + humidityDeficit*0.5` and clamped to 5–99; if you change this logic in `drought_risk.py`, mirror any derived fields (`soil_moisture_index`, `rainfall_deficit`) that the frontend renders.
- Chat responses run through Google Gemini via `chatbot.py`; continue returning `{ "response": "<text>" }` so `sendChatMessage` can fall back cleanly.

## Sidecar workflows
- Launch the observability/LLM router with `cd sidecar && python main_app.py`; monitor at http://localhost:9000 and use `python test_dashboard.py --test full` or `python simulate_load.py --pattern steady --rate 10 --duration 120` when validating changes.
- Rate limiting, routing, and worker pools live in `sidecar/rate_limiter.py`, `router.py`, and `worker.py`; when adding a provider update `providers/*.py`, `config.py`, and the routing tables documented in `README.md`.

## Developer workflow quick reference
- Frontend: `npm install` then `npm run dev` (port 5173); `npm run build` for prod bundles.
- Backend: ensure `.env` contains real API keys (`GOOGLE_API_KEY`, `OPENWEATHER_API_KEY`), then `python main.py` (port 9100).
- Sidecar: copy `.env` from `sidecar/.env.example` (if present), export Anthropic/Groq/Gemini keys, run `python main_app.py`.
- E2E smoke test: start backend + frontend, visit the map, click a region (expect forecast + trend), and send a chat message; if backend is down the UI should show “Serverless Mode,” so preserve that status triage logic in `App.tsx`.

## Integration pointers
- Adding a new metric requires: backend endpoint in `routes.py` + serializer, TypeScript type update, `services/api.ts` fetch wrapper, and UI wiring (usually `App.tsx` + a `StatusCard` or chart).
- Never hardcode URLs—derive from `API_BASE_URL` so proxying or deployment changes stay centralized.
- Log new backend errors with meaningful messages; the frontend surfaces only `"DATA_UNAVAILABLE"/"CONNECTION_REFUSED"` tokens, so keep using those strings for recoverable failures.
