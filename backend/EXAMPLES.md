"""
Example API Requests for Malaria Outbreak Forecasting API
"""

# ==================== CURL EXAMPLES ====================

# 1. ROOT/STATUS CHECK
curl http://localhost:8000/
curl http://localhost:8000/health

# 2. LOGIN
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 3. GET ALL LOCATIONS
curl http://localhost:8000/locations | python -m json.tool

# 4. FORECAST BY DISTRICT (POST)
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"district": "Bankura", "state": "West Bengal"}' | python -m json.tool

# 5. FORECAST BY DISTRICT NAME (GET)
curl "http://localhost:8000/forecast/district/Bankura?state=West%20Bengal" | python -m json.tool

# ==================== PYTHON EXAMPLES ====================

import requests
import json

BASE_URL = "http://localhost:8000"

# Login
login_response = requests.post(
    f"{BASE_URL}/login",
    json={"username": "admin", "password": "admin123"}
)
print("Login:", login_response.json())

# Get Locations
locations = requests.get(f"{BASE_URL}/locations")
print("Locations:", locations.json())

# Get Forecast
forecast = requests.post(
    f"{BASE_URL}/forecast",
    json={"district": "Bankura", "state": "West Bengal"}
)
print("Forecast:", json.dumps(forecast.json(), indent=2))

# ==================== JAVASCRIPT/FETCH EXAMPLES ====================

// Root Check
fetch('http://localhost:8000/')
  .then(r => r.json())
  .then(d => console.log(d))

// Login
fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
})
  .then(r => r.json())
  .then(d => console.log(d))

// Get Forecast
fetch('http://localhost:8000/forecast', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    district: 'Bankura',
    state: 'West Bengal'
  })
})
  .then(r => r.json())
  .then(d => console.log(JSON.stringify(d, null, 2)))

# ==================== EXPECTED RESPONSE FORMAT ====================

{
  "status": "outbreak_detected",
  "district": "Bankura",
  "state": "West Bengal",
  "message": null,
  "forecast": {
    "outbreak_status": "low_risk|moderate_risk|high_risk",
    "disease_name": "Malaria",
    "forecast_by_gender": {
      "male": <number>,
      "female": <number>
    },
    "forecast_by_age_group": {
      "children_0_5": <number>,
      "youth_5_18": <number>,
      "adults_18_60": <number>,
      "elderly_60_plus": <number>
    },
    "total_expected_cases": <number>,
    "confidence_level": 0.0-1.0,
    "recommendations": "<string>"
  }
}

# ==================== ERROR RESPONSES ====================

# No Data Found
{
  "status": "no_outbreak_observed",
  "district": "UnknownDistrict",
  "state": null,
  "message": "No outbreak data found for this district. Maintain awareness of a healthy lifestyle.",
  "forecast": null
}

# Invalid Credentials
{
  "detail": "Invalid credentials",
  "status": "error"
}

# ==================== AVAILABLE DISTRICTS ====================

Districts currently in database:
- Bankura (West Bengal)
- Etah (Uttar Pradesh)
- Karaikal (Puducherry)
- Dadra And Nagar (The Dadra And Nagar Haveli And Daman And Diu)
- Nandigram HD# (Unknown State)

Use /locations endpoint to get the complete list
