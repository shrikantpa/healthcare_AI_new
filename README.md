# Healthcare Data Analytics - Malaria Outbreak Forecasting

## Overview
A modularized FastAPI-based REST API for malaria outbreak forecasting using historical epidemiological data and AI-powered LLM forecasting (Groq LLaMA 3.3).

## Features
- **SQLite Database** with three core tables:
  - `location`: State and district information
  - `malaria_state_data`: Historical malaria cases and demographics
  - `user_mapping`: User authentication and role management
- **FastAPI REST Endpoints** for:
  - User authentication (login)
  - District data retrieval
  - Outbreak forecasting with LLM integration
- **Groq LLM Integration** for intelligent outbreak predictions
- **Forecasting Output**: JSON format with:
  - Disease name
  - Forecast by gender (male/female)
  - Forecast by age group
  - Total expected cases
  - Outbreak risk status and health awareness recommendations

## Project Structure
```
healthcare_data_analytics/
├── backend/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application
│   ├── database.py              # SQLite database manager
│   └── llm_service.py           # Groq LLM service
├── data/
│   └── maleria_data.json        # Historical malaria data (330 records)
├── venv/                        # Python virtual environment
├── .env                         # Environment variables (GROQ_API key)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
cd healthcare_data_analytics
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
The `.env` file contains:
```
GROQ_API=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
```

### 5. Run the Application
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 6. Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- **POST** `/login` - User login
  ```bash
  curl -X POST http://localhost:8000/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}'
  ```

### Data
- **GET** `/locations` - Get all available districts and states
  ```bash
  curl http://localhost:8000/locations
  ```

### Forecasting
- **POST** `/forecast` - Get outbreak forecast for a district
  ```bash
  curl -X POST http://localhost:8000/forecast \
    -H "Content-Type: application/json" \
    -d '{"district": "Kolkata", "state": "West Bengal"}'
  ```

- **GET** `/forecast/district/{district}` - Get forecast by district name
  ```bash
  curl "http://localhost:8000/forecast/district/Kolkata?state=West%20Bengal"
  ```

### Health Check
- **GET** `/health` - API health status
  ```bash
  curl http://localhost:8000/health
  ```

## Default Users
```
Username: admin    | Password: admin123    | Role: admin
Username: user     | Password: user123     | Role: viewer
Username: analyst  | Password: analyst123  | Role: analyst
```

## Forecast Response Format
```json
{
  "status": "outbreak_detected",
  "district": "Kolkata",
  "state": "West Bengal",
  "forecast": {
    "outbreak_status": "high_risk",
    "disease_name": "Malaria",
    "forecast_by_gender": {
      "male": 4541,
      "female": 6654
    },
    "forecast_by_age_group": {
      "children_0_5": 1709,
      "youth_5_18": 2279,
      "adults_18_60": 5698,
      "elderly_60_plus": 1709
    },
    "total_expected_cases": 11195,
    "confidence_level": 0.75,
    "recommendations": "Maintain awareness of a healthy lifestyle. Use mosquito nets, ensure proper sanitation, and seek medical attention if symptoms appear."
  }
}
```

## Database Information
- **Type**: SQLite
- **Location**: `backend/malaria_data.db`
- **Records**: 330 malaria cases from 2021-2024
- **Coverage**: Multiple states including Uttar Pradesh, West Bengal, Puducherry, etc.

## LLM Configuration
- **Provider**: Groq
- **Model**: llama-3.3-70b-versatile
- **Temperature**: 0 (deterministic forecasting)
- **Task**: Medical outbreak forecasting with demographic breakdown

## Technologies Used
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLite
- **LLM**: Groq (LLaMA 3.3 70B)
- **ORM/Query**: Direct SQL via sqlite3
- **Async**: Full async/await support
- **Documentation**: Auto-generated OpenAPI/Swagger

## Module Descriptions

### database.py
Handles all database operations:
- Table creation
- JSON data import
- CRUD operations
- District-specific queries

### llm_service.py
Manages Groq LLM integration:
- Prompt generation
- Response parsing
- Forecast calculation
- Error handling

### main.py
FastAPI application with:
- Route definitions
- Request/response models
- Dependency injection
- Event handlers

## Health Awareness Message
When no outbreak is detected: *"No outbreak observed. Maintain awareness of a healthy lifestyle."*
When outbreak detected: Specific recommendations with preventive measures.

## Notes
- Temperature is set to 0 for consistent, deterministic forecasting
- All endpoints return JSON responses
- CORS is enabled for cross-origin requests
- Logging enabled for debugging and monitoring

## License
See LICENSE file in the project root.