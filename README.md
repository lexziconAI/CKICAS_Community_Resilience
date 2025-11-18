# CKICAS Drought Monitor

## System Architecture
- **Frontend**: React + Vite + Leaflet (Port 5173)
- **Backend**: FastAPI + Python 3.11 + Google Gemini (Port 8001)

## Setup Instructions

### 1. Backend Setup
Navigate to the `backend` folder (you may need to move the backend files to a dedicated folder if generated in root):

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with your Google API Key:
```
GOOGLE_API_KEY=your_api_key_here
```

Run the server:
```bash
python main.py
```
Server will start at http://localhost:8001.

### 2. Frontend Setup
In the project root:

```bash
npm install
npm run dev
```
Frontend will start at http://localhost:5173.

### 3. Usage
1. Open the frontend.
2. View the map for risk levels.
3. Click a region to analyze it.
4. Chat with the Gemini AI about drought advice.
