# Quick Start Guide

## Prerequisites
- Python 3.8+
- Groq API Key (already configured in `.env`)

## Getting Started in 3 Steps

### Step 1: Navigate to Backend Directory
```bash
cd /workspaces/healthcare_data_analytics/backend
```

### Step 2: Activate Virtual Environment
```bash
source ../venv/bin/activate
```

### Step 3: Start the API Server
```bash
# Option A: Using the provided start script (Recommended)
bash start.sh

# Option B: Direct Python execution
python main.py

# Option C: Using uvicorn with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Access the API

Once running, access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **API Endpoint**: http://localhost:8000

## Test the API

### 1. Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Get Available Districts
```bash
curl http://localhost:8000/locations
```

### 3. Get Malaria Outbreak Forecast
```bash
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"district": "Bankura", "state": "West Bengal"}'
```

## Response Example

```json
{
  "status": "outbreak_detected",
  "district": "Bankura",
  "state": "West Bengal",
  "forecast": {
    "outbreak_status": "low_risk",
    "disease_name": "Malaria",
    "forecast_by_gender": {
      "male": 100,
      "female": 70
    },
    "forecast_by_age_group": {
      "children_0_5": 20,
      "youth_5_18": 40,
      "adults_18_60": 90,
      "elderly_60_plus": 20
    },
    "total_expected_cases": 170,
    "confidence_level": 0.8,
    "recommendations": "Maintain health awareness..."
  }
}
```

## Default Login Credentials

```
Username: admin
Password: admin123
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── database.py             # SQLite database manager
├── llm_service.py          # Groq LLM integration
├── malaria_data.db         # SQLite database (auto-created)
├── start.sh                # Quick start script
└── EXAMPLES.md             # More examples
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database Errors
- Delete `backend/malaria_data.db`
- Restart the application (it will recreate)

### GROQ API Errors
- Verify `.env` file has valid GROQ_API key
- Check internet connection
- Verify API quota hasn't been exceeded

## Next Steps

See full documentation in:
- `README.md` - Complete system documentation
- `SETUP_SUMMARY.txt` - Detailed setup information
- `EXAMPLES.md` - API request examples
