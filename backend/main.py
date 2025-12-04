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

class UserLoginResponse(BaseModel):
    user_id: int
    username: str
    role: str
    district: Optional[str] = None
    state: Optional[str] = None

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    district: str
    state: str
    role: str

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

class RoleBasedGuidanceRequest(BaseModel):
    username: str
    password: str
    district: Optional[str] = None
    state: Optional[str] = None

class RoleBasedGuidanceResponse(BaseModel):
    status: str
    username: str
    role: str
    district: Optional[str] = None
    state: Optional[str] = None
    forecast: Optional[dict] = None
    guidance: Optional[dict] = None
    message: str

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

@app.post("/login", response_model=UserLoginResponse, tags=["Authentication"])
async def login(user: UserLogin):
    """
    User login endpoint
    
    Args:
        user: UserLogin object with username and password
        
    Returns:
        UserLoginResponse with user details including location
    """
    try:
        # Verify user credentials from user_mapping
        db_manager.cursor.execute(
            'SELECT user_id, username, role FROM user_mapping WHERE username = ? AND password = ?',
            (user.username, user.password)
        )
        user_record = db_manager.cursor.fetchone()
        
        if not user_record:
            logger.warning(f"Failed login attempt for user {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_id, username, role = user_record[0], user_record[1], user_record[2]
        
        # Try to get location data from users table
        district = None
        state = None
        db_manager.cursor.execute(
            'SELECT district, state FROM users WHERE username = ?',
            (username,)
        )
        user_profile = db_manager.cursor.fetchone()
        if user_profile:
            district, state = user_profile[0], user_profile[1]
        
        logger.info(f"User {username} logged in successfully")
        return UserLoginResponse(
            user_id=user_id,
            username=username,
            role=role,
            district=district,
            state=state
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")

@app.post("/signup", response_model=UserSignupResponse, tags=["Authentication"])
async def signup(user_data: UserSignup):
    """
    User signup endpoint with location validation
    
    Creates a new user profile after verifying that the provided district and state
    exist in the location table. The user's role will be assigned based on the provided value.
    
    Args:
        user_data: UserSignup object with:
            - first_name: User's first name
            - last_name: User's last name
            - username: Username for login (must be unique)
            - password: User's password
            - district: District name (must exist in location table)
            - state: State name (must match the district)
            - role: User role (ASHA, DCMO, SCMO)
            
    Returns:
        UserSignupResponse with new user details if successful
        
    Raises:
        HTTPException 400: If district/state combination not found in location table
        HTTPException 400: If username already exists
        HTTPException 400: If role is invalid
        HTTPException 500: If database error occurs
    """
    try:
        logger.info(f"Signup request for user: {user_data.username}, location: {user_data.district}, {user_data.state}, role: {user_data.role}")
        
        # Validate role
        valid_roles = ['ASHA', 'DCMO', 'SCMO']
        if user_data.role not in valid_roles:
            logger.warning(f"Invalid role provided: {user_data.role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Verify location exists
        location_id = db_manager.verify_location(user_data.district, user_data.state)
        
        if not location_id:
            logger.warning(f"Location not found: {user_data.district}, {user_data.state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location not found: District '{user_data.district}' in State '{user_data.state}' does not exist in the system"
            )
        
        # Create user with role
        new_user = db_manager.create_user(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            password=user_data.password,
            district=user_data.district,
            state=user_data.state,
            role=user_data.role
        )
        
        if not new_user:
            logger.warning(f"Failed to create user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_data.username}' already exists or database error occurred"
            )
        
        logger.info(f"User {user_data.username} created successfully with role {user_data.role}")
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

@app.post("/guidance", response_model=RoleBasedGuidanceResponse, tags=["Guidance"])
async def get_role_based_guidance(request: RoleBasedGuidanceRequest):
    """
    Get role-specific guidance for disease outbreak management
    
    This endpoint:
    1. Authenticates the user
    2. Fetches forecast data for the district/state
    3. Generates role-specific guidance based on user role (ASHA, DCMO, SCMO)
    
    For ASHA (Health Worker):
    - General remedies for disease prevention
    - Social remedies for community-level intervention
    - Government regulatory actions
    - Healthcare body actions
    
    For DCMO (District Chief Medical Officer):
    - Cases identified so far
    - Healthcare department actions
    - High-level inventory arrangements
    - District-level resource management
    
    For SCMO (State Chief Medical Officer):
    - State-level results and infected districts
    - Comparative analysis of all districts
    - State-level remedies and initiatives
    - Emergency funding and deployment of medical professionals
    
    Args:
        request: RoleBasedGuidanceRequest with username, password, and optional location
        
    Returns:
        RoleBasedGuidanceResponse with forecast and role-specific guidance
    """
    try:
        logger.info(f"Guidance request from user: {request.username}")
        
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id, username, role FROM user_mapping WHERE username = ? AND password = ?',
            (request.username, request.password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            logger.warning(f"Authentication failed for user: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user_id, username, user_role = user[0], user[1], user[2]
        logger.info(f"✓ User authenticated: {username}, Role: {user_role}")
        
        # Get district and state - for SCMO, get from signed-up user profile if available
        district = request.district
        state_name = request.state
        
        if not district or not state_name:
            # Try to get from user profile (users table)
            db_manager.cursor.execute(
                'SELECT district, state FROM users WHERE username = ?',
                (username,)
            )
            user_profile = db_manager.cursor.fetchone()
            if user_profile:
                district = district or user_profile[0]
                state_name = state_name or user_profile[1]
        
        if not district or not state_name:
            logger.warning(f"District or state not provided for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="District and state are required for guidance"
            )
        
        logger.info(f"Generating guidance for: {district}, {state_name}, Role: {user_role}")
        
        # Fetch forecast data
        forecast_result = _get_forecast_for_guidance(district, state_name, user_role)
        
        if not forecast_result or forecast_result.get('status') == 'error':
            logger.warning(f"No forecast data found for {district}")
            return RoleBasedGuidanceResponse(
                status="no_data",
                username=username,
                role=user_role,
                district=district,
                state=state_name,
                forecast=None,
                guidance=None,
                message="No outbreak data found for the specified location"
            )
        
        # Generate role-specific guidance
        guidance_result = _generate_role_specific_guidance(
            user_role=user_role,
            forecast_data=forecast_result,
            district=district,
            state=state_name
        )
        
        logger.info(f"✓ Guidance generated successfully for {username} ({user_role})")
        
        return RoleBasedGuidanceResponse(
            status="success",
            username=username,
            role=user_role,
            district=district,
            state=state_name,
            forecast=forecast_result.get('forecast'),
            guidance=guidance_result,
            message=f"Role-specific guidance generated for {user_role}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating guidance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating guidance: {str(e)}")

# ==================== Helper Functions ====================

def _get_forecast_for_guidance(district: str, state: str, role: str) -> dict:
    """
    Get forecast data for guidance generation
    
    For SCMO role, gets data for all districts in the state
    For ASHA and DCMO, gets data for the specific district
    """
    try:
        if role == 'SCMO':
            # Get all districts in the state
            db_manager.cursor.execute(
                'SELECT DISTINCT district FROM location WHERE state = ?',
                (state,)
            )
            districts = db_manager.cursor.fetchall()
            
            if not districts:
                return {'status': 'error', 'message': 'No districts found for state'}
            
            # Get forecast for each district
            state_forecast = {
                'status': 'state_level_analysis',
                'state': state,
                'districts': []
            }
            
            for (dist,) in districts:
                district_data = db_manager.get_district_data(dist, state)
                if district_data and 'years' in district_data and len(district_data['years']) > 0:
                    forecast = llm_service.generate_outbreak_forecast(district_data)
                    state_forecast['districts'].append({
                        'district': dist,
                        'forecast': forecast.get('forecast')
                    })
            
            return {
                'status': 'success',
                'forecast': state_forecast
            }
        else:
            # For ASHA and DCMO - get specific district data
            district_data = db_manager.get_district_data(district, state)
            
            if not district_data or 'years' not in district_data or len(district_data['years']) == 0:
                return {'status': 'error', 'message': 'No data found for district'}
            
            forecast = llm_service.generate_outbreak_forecast(district_data)
            
            return {
                'status': 'success',
                'forecast': forecast.get('forecast')
            }
            
    except Exception as e:
        logger.error(f"Error getting forecast for guidance: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def _generate_role_specific_guidance(user_role: str, forecast_data: dict, district: str, state: str) -> dict:
    """
    Generate role-specific guidance based on forecast data and user role
    """
    try:
        forecast = forecast_data.get('forecast')
        
        if not forecast:
            return {'error': 'No forecast data available'}
        
        if user_role == 'ASHA':
            return _generate_asha_guidance(forecast, district, state)
        elif user_role == 'DCMO':
            return _generate_dcmo_guidance(forecast, district, state)
        elif user_role == 'SCMO':
            return _generate_scmo_guidance(forecast, district, state)
        else:
            return {'error': f'Unknown role: {user_role}'}
            
    except Exception as e:
        logger.error(f"Error generating role-specific guidance: {str(e)}")
        return {'error': str(e)}

def _generate_asha_guidance(forecast: dict, district: str, state: str) -> dict:
    """
    Generate ASHA worker level guidance
    ASHA focus: Community-level prevention and awareness
    """
    try:
        outbreak_status = forecast.get('outbreak_status', 'low_risk')
        total_cases = forecast.get('total_expected_cases', 0)
        
        prompt = f"""
Based on the malaria outbreak forecast for {district}, {state}, generate ASHA worker guidance.

Outbreak Status: {outbreak_status}
Expected Cases: {total_cases}

Please provide guidance in JSON format with these 4 components:

{{
    "general_remedies": "Provide specific remedies and preventive measures that individuals can follow to remain healthy and avoid malaria infection (e.g., proper sleep, balanced diet, mosquito prevention, sanitation)",
    "social_remedies": "Provide community-level interventions and mass-scale initiatives that can be implemented (e.g., community awareness camps, mass distribution of mosquito nets, neighborhood sanitation drives)",
    "govt_regulatory_actions": "Provide actions that government agencies should take (e.g., conducting medical camps, awareness sessions, educational programs, inspection of water sources)",
    "healthcare_body_actions": "Provide actions that healthcare facilities should take (e.g., stockpiling medicines, testing kits availability, ensuring adequate beds, doctor availability, nursing staff deployment, vaccination programs)"
}}

IMPORTANT: Return ONLY valid JSON with these 4 fields. Make recommendations specific to the current outbreak status and expected cases.
"""
        
        response = llm_service.generate_response(prompt)
        
        # Parse the response
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            guidance = json.loads(json_match.group(0))
            return guidance
        else:
            return {
                "general_remedies": "Use mosquito nets, apply mosquito repellent, maintain clean surroundings",
                "social_remedies": "Organize community awareness camps, distribute mosquito nets, conduct neighborhood cleaning drives",
                "govt_regulatory_actions": "Conduct free medical camps, run awareness sessions, inspect breeding grounds for mosquitoes",
                "healthcare_body_actions": "Maintain adequate stock of antimalarial drugs, ensure testing kits availability, have sufficient beds and medical staff"
            }
    except Exception as e:
        logger.error(f"Error generating ASHA guidance: {str(e)}")
        return {
            "error": str(e),
            "general_remedies": "Contact healthcare provider for guidance",
            "social_remedies": "Coordinate with local authorities",
            "govt_regulatory_actions": "Report to government health department",
            "healthcare_body_actions": "Consult with healthcare facilities"
        }

def _generate_dcmo_guidance(forecast: dict, district: str, state: str) -> dict:
    """
    Generate DCMO (District Chief Medical Officer) level guidance
    DCMO focus: District-level resource management and healthcare arrangements
    """
    try:
        outbreak_status = forecast.get('outbreak_status', 'low_risk')
        total_cases = forecast.get('total_expected_cases', 0)
        male_cases = forecast.get('forecast_by_gender', {}).get('male', 0)
        female_cases = forecast.get('forecast_by_gender', {}).get('female', 0)
        
        prompt = f"""
Generate DCMO (District Chief Medical Officer) level action plan for {district}, {state}.

Outbreak Status: {outbreak_status}
Cases Identified So Far: {total_cases}
Male Cases: {male_cases}
Female Cases: {female_cases}

As DCMO, provide a high-level inventory and resource arrangement plan in JSON format:

{{
    "cases_identified": {total_cases},
    "department_actions": "List healthcare department initiatives and actions taken (e.g., mobilizing healthcare teams, setting up testing centers, activating surveillance systems)",
    "inventory_arrangements": "Provide high-level inventory management plan (e.g., quantitative requirements for medicines, testing kits, PPE, beds, ventilators)",
    "resource_deployment": "Resource allocation strategy (e.g., number of doctors, nurses, paramedics needed, establishment of testing centers, quarantine facilities)",
    "coordination_plan": "Inter-departmental coordination with other authorities for district-level response",
    "budget_allocation": "Estimated budget requirements for the response"
}}

IMPORTANT: Return ONLY valid JSON. Focus on district-level resource management, not community level. Be specific about quantities and deployment.
"""
        
        response = llm_service.generate_response(prompt)
        
        # Parse the response
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            guidance = json.loads(json_match.group(0))
            return guidance
        else:
            return {
                "cases_identified": total_cases,
                "department_actions": "Activate healthcare surveillance, mobilize medical teams, establish testing centers",
                "inventory_arrangements": f"Prepare for {total_cases} cases: {int(total_cases*2)} antimalarial doses, {int(total_cases*1.5)} testing kits, appropriate beds",
                "resource_deployment": f"Deploy {int(total_cases/50)} doctors, {int(total_cases/30)} nurses, {int(total_cases/20)} paramedics across district",
                "coordination_plan": "Coordinate with district administration, police, and local authorities for compliance",
                "budget_allocation": f"Estimated budget: Rs. {int(total_cases*500)} for medicines and equipment"
            }
    except Exception as e:
        logger.error(f"Error generating DCMO guidance: {str(e)}")
        return {
            "error": str(e),
            "cases_identified": 0,
            "department_actions": "Consult with state health department",
            "inventory_arrangements": "Maintain adequate stock at district level",
            "resource_deployment": "Deploy available healthcare resources",
            "coordination_plan": "Coordinate with all stakeholders",
            "budget_allocation": "Allocate as per state guidelines"
        }

def _generate_scmo_guidance(forecast: dict, district: str, state: str) -> dict:
    """
    Generate SCMO (State Chief Medical Officer) level guidance
    SCMO focus: State-level analysis, inter-district coordination, emergency measures
    """
    try:
        prompt = f"""
Generate SCMO (State Chief Medical Officer) level strategic plan for the state of {state}.

The forecast data includes district-wise analysis showing which districts are heavily infected.

Provide a state-level strategic response in JSON format:

{{
    "state_overview": "Summary of outbreak status across the state",
    "highly_affected_districts": "List of districts most badly infected with severity ranking",
    "comparative_analysis": "Analysis comparing district-wise infection rates and trends",
    "state_level_remedies": "State-wide initiatives and countermeasures",
    "medical_professional_deployment": "Strategy for deploying doctors, paramedics, and army medical personnel to high-risk districts",
    "emergency_measures": "Emergency protocols and resource mobilization",
    "inter_district_coordination": "Coordination strategy between districts for resource sharing",
    "emergency_funding": "Recommendation for emergency fund sanctioning and allocation",
    "timeline_and_milestones": "Phased implementation plan with timelines"
}}

IMPORTANT: Return ONLY valid JSON. Focus on state-level strategic decisions, resource allocation across districts, and emergency measures.
"""
        
        response = llm_service.generate_response(prompt)
        
        # Parse the response
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            guidance = json.loads(json_match.group(0))
            return guidance
        else:
            return {
                "state_overview": f"Malaria outbreak management for {state}",
                "highly_affected_districts": "Identify and prioritize high-risk districts from forecast data",
                "comparative_analysis": "Compare infection rates across all districts in the state",
                "state_level_remedies": "Launch state-wide public health campaigns, strengthen healthcare infrastructure",
                "medical_professional_deployment": "Deploy additional doctors and paramedics to high-risk districts, coordinate with Army Medical Corps",
                "emergency_measures": "Activate emergency response protocols, establish rapid testing centers, mobilize quarantine facilities",
                "inter_district_coordination": "Facilitate resource sharing between better-resourced and under-resourced districts",
                "emergency_funding": "Recommend emergency fund sanctioning for outbreak response",
                "timeline_and_milestones": "Phase 1: Assessment (Week 1), Phase 2: Deployment (Week 2-3), Phase 3: Monitoring (Ongoing)"
            }
    except Exception as e:
        logger.error(f"Error generating SCMO guidance: {str(e)}")
        return {
            "error": str(e),
            "state_overview": "State-level outbreak management",
            "highly_affected_districts": "Pending analysis",
            "comparative_analysis": "Pending comparison",
            "state_level_remedies": "Activate state health response",
            "medical_professional_deployment": "Deploy resources as needed",
            "emergency_measures": "Implement emergency protocols",
            "inter_district_coordination": "Coordinate across districts",
            "emergency_funding": "Request emergency allocation",
            "timeline_and_milestones": "To be determined based on situation"
        }

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
