"""
FastAPI REST API for Healthcare Data Analytics - Malaria Outbreak Forecasting
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Import custom modules
from database import DatabaseManager
from llm_service import LLMService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Malaria Outbreak Forecast API",
    description="REST API for malaria outbreak forecasting using historical data and LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and LLM service
db_manager = DatabaseManager()
llm_service = LLMService()

# ==================== Pydantic Models ====================

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    district: str
    state: str

class UserSignupResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    username: str
    district: str
    state: str
    role: str
    created_at: Optional[str] = None

class ForecastRequest(BaseModel):
    district: str
    state: Optional[str] = None

class LocationResponse(BaseModel):
    state: str
    district: str

class ForecastResponse(BaseModel):
    status: str
    district: str
    state: Optional[str]
    message: Optional[str] = None
    forecast: Optional[dict] = None

# ==================== Dependencies ====================

def get_current_user(username: str, password: str) -> UserResponse:
    """Verify user credentials"""
    db_manager.cursor.execute(
        'SELECT user_id, username, role FROM user_mapping WHERE username = ? AND password = ?',
        (username, password)
    )
    user = db_manager.cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return UserResponse(user_id=user[0], username=user[1], role=user[2])

# ==================== API Endpoints ====================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status check"""
    return {
        "status": "active",
        "message": "Malaria Outbreak Forecast API is running",
        "version": "1.0.0"
    }

@app.post("/login", response_model=UserResponse, tags=["Authentication"])
async def login(user: UserLogin):
    """
    User login endpoint
    
    Args:
        user: UserLogin object with username and password
        
    Returns:
        UserResponse with user details
    """
    try:
        current_user = get_current_user(user.username, user.password)
        logger.info(f"User {user.username} logged in successfully")
        return current_user
    except HTTPException as e:
        logger.warning(f"Failed login attempt for user {user.username}")
        raise e

@app.post("/signup", response_model=UserSignupResponse, tags=["Authentication"])
async def signup(user_data: UserSignup):
    """
    User signup endpoint with location validation
    
    Creates a new user profile after verifying that the provided district and state
    exist in the location table. The user will be assigned the 'analyst' role.
    
    Args:
        user_data: UserSignup object with:
            - first_name: User's first name
            - last_name: User's last name
            - username: Username for login (must be unique)
            - password: User's password
            - district: District name (must exist in location table)
            - state: State name (must match the district)
            
    Returns:
        UserSignupResponse with new user details if successful
        
    Raises:
        HTTPException 400: If district/state combination not found in location table
        HTTPException 400: If username already exists
        HTTPException 500: If database error occurs
    """
    try:
        logger.info(f"Signup request for user: {user_data.username}, location: {user_data.district}, {user_data.state}")
        
        # Verify location exists
        location_id = db_manager.verify_location(user_data.district, user_data.state)
        
        if not location_id:
            logger.warning(f"Location not found: {user_data.district}, {user_data.state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location not found: District '{user_data.district}' in State '{user_data.state}' does not exist in the system"
            )
        
        # Create user
        new_user = db_manager.create_user(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            password=user_data.password,
            district=user_data.district,
            state=user_data.state
        )
        
        if not new_user:
            logger.warning(f"Failed to create user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_data.username}' already exists or database error occurred"
            )
        
        logger.info(f"User {user_data.username} created successfully")
        return UserSignupResponse(**new_user)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")

@app.get("/locations", response_model=List[LocationResponse], tags=["Data"])
async def get_all_locations():
    """
    Get all available districts and states
    
    Returns:
        List of locations (state, district pairs)
    """
    try:
        locations = db_manager.get_all_districts()
        return [LocationResponse(**loc) for loc in locations]
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching locations")

@app.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def get_outbreak_forecast(request: ForecastRequest):
    """
    Get malaria outbreak forecast for a specific district
    
    This endpoint queries the database for historical malaria data and uses
    Groq LLM to generate outbreak forecasts including:
    - Disease name
    - Forecast by gender (male/female)
    - Forecast by age group
    - Total expected cases
    - Risk status and recommendations
    
    Args:
        request: ForecastRequest containing district and optional state
        
    Returns:
        ForecastResponse with outbreak forecast data in JSON format
    """
    try:
        logger.info(f"Forecast request for district: {request.district}, state: {request.state}")
        
        # Get district data from database
        district_data = db_manager.get_district_data(request.district, request.state)
        
        if not district_data or 'years' not in district_data or len(district_data['years']) == 0:
            logger.info(f"No data found for district: {request.district}")
            return ForecastResponse(
                status="no_outbreak_observed",
                district=request.district,
                state=request.state,
                message="No outbreak observed. Please spread awareness for a healthy lifestyle.",
                forecast=None
            )
        
        # Generate forecast using LLM
        forecast_result = llm_service.generate_outbreak_forecast(district_data)
        
        return ForecastResponse(
            status=forecast_result.get('status'),
            district=forecast_result.get('district', request.district),
            state=forecast_result.get('state', request.state),
            message=forecast_result.get('message', 'Alert, there is a potential outbreak observed.'),
            forecast=forecast_result.get('forecast')
        )
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@app.get("/forecast/district/{district}", response_model=ForecastResponse, tags=["Forecasting"])
async def get_forecast_by_district_name(district: str, state: Optional[str] = None):
    """
    Get outbreak forecast by district name (alternative endpoint)
    
    Args:
        district: District name (URL parameter)
        state: Optional state name (query parameter)
        
    Returns:
        ForecastResponse with forecast data
    """
    request = ForecastRequest(district=district, state=state)
    return await get_outbreak_forecast(request)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_service": "initialized"
    }

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )

# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        db_manager.create_tables()
        
        # Check if data already loaded
        db_manager.cursor.execute('SELECT COUNT(*) FROM malaria_state_data')
        count = db_manager.cursor.fetchone()[0]
        
        if count == 0:
            logger.info("Loading malaria data from JSON...")
            # Use parent directory to access data folder
            import os
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "maleria_data.json")
            db_manager.load_json_data(data_path)
        else:
            logger.info(f"Database already contains {count} records")
        
        # Add default users
        db_manager.add_default_users()
        
        logger.info("✓ Database initialization complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        db_manager.close()
        logger.info("✓ Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
