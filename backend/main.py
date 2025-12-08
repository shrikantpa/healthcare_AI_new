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
    username: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    created_at: Optional[str] = None
    password: Optional[str] = None

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

class OutbreakCheckRequest(BaseModel):
    username: str
    password: str
    district: Optional[str] = None
    state: Optional[str] = None

class OutbreakCheckResponse(BaseModel):
    status: str
    username: str
    role: str
    district: str
    state: str
    outbreak_detected: bool
    forecast: Optional[dict] = None
    message: str

class ActionRequest(BaseModel):
    username: str
    password: str
    district: Optional[str] = None
    state: Optional[str] = None
    question: Optional[str] = None

class ActionResponse(BaseModel):
    status: str
    username: str
    role: str
    district: str
    state: str
    forecast: Optional[dict] = None
    actions: Optional[dict] = None
    message: str

class ServiceRequestItem(BaseModel):
    request_item: str
    request_details: Optional[str] = None

class ServiceRequestResponse(BaseModel):
    status: str
    request_id: int
    message: str

class EscalateServiceRequestResponse(BaseModel):
    status: str
    request_id: int
    escalation_level: int
    message: str

# ==================== Dependencies ====================

def get_current_user(username: str, password: str) -> UserResponse:
    """Verify user credentials"""
    db_manager.cursor.execute(
        'SELECT user_id, username, role FROM users WHERE username = ? AND password = ?',
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
        UserLoginResponse with complete user details
    """
    try:
        username = user.username
        password = user.password
        first_name = None
        last_name = None
        district = None
        state = None
        created_at = None
        db_manager.cursor.execute(
            'SELECT first_name, last_name, district, state, role, created_at FROM users WHERE username = ? and password = ?',
            (username, password)
        )
        user_profile = db_manager.cursor.fetchone()
        if user_profile:
            first_name, last_name, district, state, role, created_at = user_profile[0], user_profile[1], user_profile[2], user_profile[3], user_profile[4], user_profile[5]
        
        logger.info(f"User {username} logged in successfully with role {role}")
        return UserLoginResponse(
            user_id = 1,
            username=username,
            role=role,
            first_name=first_name,
            last_name=last_name,
            district=district,
            state=state,
            created_at=created_at,
            password=user.password
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
        forecast_result['forecast']['outbreak_status'] = "very high"
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
            'SELECT user_id, username, role FROM users WHERE username = ? AND password = ?',
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

def _generate_role_specific_actions(user_role: str, forecast_data: dict, district: str, state: str, question: Optional[str] = None) -> dict:
    """
    Generate role-specific actions based on forecast data
    Uses simplified, targeted prompts for each role
    """
    try:
        if not forecast_data:
            return {'error': 'No forecast data available'}
        
        if user_role == 'ASHA':
            return _generate_asha_actions(forecast_data, district, state, question)
        elif user_role == 'DCMO':
            return _generate_dcmo_actions(forecast_data, district, state, question)
        elif user_role == 'SCMO':
            return _generate_scmo_actions(forecast_data, district, state, question)
        else:
            return {'error': f'Unknown role: {user_role}'}
            
    except Exception as e:
        logger.error(f"Error generating role-specific actions: {str(e)}")
        return {'error': str(e)}

def _generate_asha_actions(forecast: dict, district: str, state: str, question: Optional[str] = None) -> dict:
    """Generate ASHA (health worker) specific actions - 4 components"""
    try:
        total_cases = forecast.get('total_expected_cases', 0)
        outbreak_status = forecast.get('outbreak_status', 'low_risk')
        
        prompt = f"""
You are an ASHA worker (community health worker) in {district}, {state}.

Outbreak Status: {outbreak_status}
Expected Cases: {total_cases}

Generate CONCISE recommendations in 4 categories (keep each under 50 words):

{{
    "general_remedies": "Health practices individuals should follow (sleep, diet, hygiene, prevention)",
    "social_remedies": "Community-scale initiatives (awareness camps, mosquito nets distribution, cleaning drives)",
    "govt_regulatory_actions": "Government actions needed (camps, awareness, inspection of water sources)",
    "healthcare_body_actions": "Healthcare facility requirements (medicines, testing kits, beds, doctors, staff, vaccination)"
}}

Return ONLY valid JSON. Be specific and actionable.
"""
        
        response = llm_service.generate_response(prompt)
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {
                "general_remedies": "Use mosquito nets, apply repellent, maintain hygiene",
                "social_remedies": "Organize community awareness camps and mosquito net distribution",
                "govt_regulatory_actions": "Conduct free medical camps and awareness sessions",
                "healthcare_body_actions": "Stock antimalarial drugs, ensure testing kits and beds available"
            }
    except Exception as e:
        logger.error(f"Error generating ASHA actions: {str(e)}")
        return {
            "general_remedies": "Contact healthcare provider",
            "social_remedies": "Coordinate with community",
            "govt_regulatory_actions": "Report to health department",
            "healthcare_body_actions": "Ensure healthcare facility readiness"
        }

def _generate_dcmo_actions(forecast: dict, district: str, state: str, question: Optional[str] = None) -> dict:
    """Generate DCMO (District Medical Officer) specific actions - 6 components"""
    try:
        total_cases = forecast.get('total_expected_cases', 0)
        male_cases = forecast.get('forecast_by_gender', {}).get('male', 0)
        female_cases = forecast.get('forecast_by_gender', {}).get('female', 0)
        
        prompt = f"""
You are DCMO (District Medical Officer) for {district}, {state}.

Cases Expected: {total_cases} (Male: {male_cases}, Female: {female_cases})

Generate CONCISE district-level action plan in 6 categories (keep each under 100 words):

{{
    "cases_identified": "Current count: {total_cases}",
    "department_actions": "Healthcare department initiatives and deployment",
    "inventory_arrangements": "Required medicines, kits, beds quantities",
    "resource_deployment": "Number of doctors, nurses, paramedics needed",
    "coordination_plan": "Coordination with administration and local authorities"
}}

Return ONLY valid JSON. Focus on district-level resource management. ###table...!!!!####
"""
        
        response = llm_service.generate_response(prompt)
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {
                "cases_identified": f"{total_cases} cases expected",
                "department_actions": "Activate healthcare teams and testing centers",
                "inventory_arrangements": f"Prepare for {total_cases} cases: medicines, testing kits, beds",
                "resource_deployment": f"Deploy {int(total_cases/50)} doctors, {int(total_cases/30)} nurses",
                "coordination_plan": "Coordinate with district administration",
            }
    except Exception as e:
        logger.error(f"Error generating DCMO actions: {str(e)}")
        return {
            "cases_identified": "0 cases",
            "department_actions": "Pending analysis",
            "inventory_arrangements": "Assess requirements",
            "resource_deployment": "Deploy as needed",
            "coordination_plan": "Coordinate with authorities",
            "budget_allocation": "Pending allocation"
        }

def _generate_scmo_actions(forecast: dict, district: str, state: str, question: Optional[str] = None) -> dict:
    """Generate SCMO (State Medical Officer) specific actions - 9 components"""
    try:
        prompt = f"""
You are SCMO (State Medical Officer) for {state}.

Generate CONCISE state-level strategic response in 9 categories (select any top-5 most relevant, keep each under 100 words  ):

{{
    "state_overview": "Overall outbreak status across the state",
    "highly_affected_districts": "Top 3-5 most affected districts with severity",
    "comparative_analysis": "District-wise comparison of infection rates",
    "budget_allocation": "Estimated budget requirement"
    "state_level_remedies": "State-wide public health initiatives",
    "medical_professional_deployment": "Deploy doctors, paramedics, army medical corps to high-risk areas",
    "emergency_measures": "Emergency protocols and quarantine facilities",
    "inter_district_coordination": "Resource sharing and support between districts",
    "emergency_funding": "Emergency fund sanctioning recommendation",
    "timeline_and_milestones": "Phased implementation: Week 1-2 (assessment), Week 2-4 (deployment)"
}}

Return ONLY valid JSON. Focus on state-level strategic decisions.
"""
        
        response = llm_service.generate_response(prompt)
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {
                "state_overview": "Outbreak management for the state",
                "highly_affected_districts": "Identify high-risk districts",
                "comparative_analysis": "Compare infection rates across districts",
                "state_level_remedies": "Launch state-wide health campaigns",
                "medical_professional_deployment": "Deploy medical personnel to high-risk areas",
                "emergency_measures": "Activate emergency response protocols",
                "inter_district_coordination": "Facilitate inter-district resource sharing",
                "emergency_funding": "Sanction emergency funds",
                "timeline_and_milestones": "Phase 1: Assessment, Phase 2: Deployment, Phase 3: Monitoring"
            }
    except Exception as e:
        logger.error(f"Error generating SCMO actions: {str(e)}")
        return {
            "state_overview": "State-level outbreak management",
            "highly_affected_districts": "Pending analysis",
            "comparative_analysis": "Pending comparison",
            "state_level_remedies": "Activate state health response",
            "medical_professional_deployment": "Deploy resources",
            "emergency_measures": "Implement protocols",
            "inter_district_coordination": "Coordinate",
            "emergency_funding": "Request funds",
            "timeline_and_milestones": "To be determined"
        }

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

@app.post("/outbreak-check", response_model=OutbreakCheckResponse, tags=["Forecasting"])
async def check_outbreak(request: OutbreakCheckRequest):
    """
    Check if outbreak is present in district - returns ONLY outbreak count data
    NO guidance, only forecast summary with counts
    
    Args:
        request: OutbreakCheckRequest with username, password, district, state
        
    Returns:
        OutbreakCheckResponse with only outbreak detection and counts
    """
    try:
        logger.info(f"Outbreak check request from user: {request.username}")
        
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id, username, role FROM users WHERE username = ? AND password = ?',
            (request.username, request.password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id, username, user_role = user[0], user[1], user[2]
        
        # Get district and state from user profile
        db_manager.cursor.execute(
            'SELECT district, state FROM users WHERE username = ?',
            (username,)
        )
        user_profile = db_manager.cursor.fetchone()
        
        if not user_profile:
            raise HTTPException(status_code=400, detail="User profile not found")
        
        district = user_profile[0]
        state_name = user_profile[1]
        
        # Get forecast data
        district_data = db_manager.get_district_data(district, state_name)
        
        if not district_data or 'years' not in district_data or len(district_data['years']) == 0:
            return OutbreakCheckResponse(
                status="no_outbreak",
                username=username,
                role=user_role,
                district=district,
                state=state_name,
                outbreak_detected=False,
                forecast=None,
                message="No outbreak observed in this district"
            )
        
        # Generate forecast (includes counts only, no guidance)
        forecast_result = llm_service.generate_outbreak_forecast_number(district_data)
        
        outbreak_detected = forecast_result.get('status') != 'no_outbreak_observed'
        return OutbreakCheckResponse(
            status="success",
            username=username,
            role=user_role,
            district=district,
            state=state_name,
            outbreak_detected=outbreak_detected,
            forecast=forecast_result.get('forecast'),
            message=f"Outbreak {'detected' if outbreak_detected else 'not detected'} in {district}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error checking outbreak: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/action", response_model=ActionResponse, tags=["Actions"])
async def get_actions(request: ActionRequest):
    """
    Get role-specific actions/guidance based on outbreak
    Invokes forecast first, then generates role-specific actions based on prompts
    
    For ASHA:
    - General remedies (individual prevention)
    - Social remedies (community-scale initiatives)
    - Government regulatory actions
    - Healthcare body actions
    
    For DCMO:
    - Cases identified (count)
    - Department actions
    - Inventory arrangements (high-level)
    - Resource deployment
    - Coordination plan
    - Budget allocation
    
    For SCMO:
    - State overview
    - Highly affected districts
    - Comparative analysis
    - State-level remedies
    - Medical professional deployment
    - Emergency measures
    - Inter-district coordination
    - Emergency funding
    - Timeline and milestones
    
    Args:
        request: ActionRequest with username, password, optional question
        
    Returns:
        ActionResponse with forecast and role-specific actions
    """
    try:
        logger.info(f"Action request from user: {request.username}")
        
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id, username, role FROM users WHERE username = ? AND password = ?',
            (request.username, request.password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id, username, user_role = user[0], user[1], user[2]
        
        # Get district and state from user profile
        db_manager.cursor.execute(
            'SELECT district, state FROM users WHERE username = ?',
            (username,)
        )
        user_profile = db_manager.cursor.fetchone()
        
        if not user_profile:
            raise HTTPException(status_code=400, detail="User profile not found")
        
        district = user_profile[0]
        state_name = user_profile[1]
        
        # Get forecast data
        district_data = db_manager.get_district_data(district, state_name)
        
        if not district_data or 'years' not in district_data or len(district_data['years']) == 0:
            return ActionResponse(
                status="no_data",
                username=username,
                role=user_role,
                district=district,
                state=state_name,
                forecast=None,
                actions=None,
                message="No outbreak data found"
            )
        
        # Generate forecast
        forecast_result = llm_service.generate_outbreak_forecast(district_data)
        forecast = forecast_result.get('forecast')
        
        # Generate role-specific actions
        actions = _generate_role_specific_actions(
            user_role=user_role,
            forecast_data=forecast,
            district=district,
            state=state_name,
            question=request.question
        )
        
        return ActionResponse(
            status="success",
            username=username,
            role=user_role,
            district=district,
            state=state_name,
            forecast=forecast,
            actions=actions,
            message=f"Actions generated for {user_role}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating actions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/service-request", response_model=ServiceRequestResponse, tags=["Service"])
async def submit_service_request(username: str, password: str, request: ServiceRequestItem):
    """
    Submit a service request for required items/resources
    Stores in service_requests table
    
    Args:
        username: Username
        password: Password
        request: ServiceRequestItem with item name and details
        
    Returns:
        ServiceRequestResponse with request_id
    """
    try:
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id, username, role FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id, username, user_role = user[0], user[1], user[2]
        
        # Get user profile
        db_manager.cursor.execute(
            'SELECT district, state FROM users WHERE username = ?',
            (username,)
        )
        user_profile = db_manager.cursor.fetchone()
        
        if not user_profile:
            raise HTTPException(status_code=400, detail="User profile not found")
        
        district = user_profile[0]
        state_name = user_profile[1]
        
        # Insert service request
        db_manager.cursor.execute('''
            INSERT INTO service_requests 
            (user_id, username, role, district, state, request_item, request_details, status, escalation_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0)
        ''', (user_id, username, user_role, district, state_name, request.request_item, request.request_details))
        
        db_manager.conn.commit()
        
        request_id = db_manager.cursor.lastrowid
        
        logger.info(f"Service request {request_id} created for {username}")
        
        return ServiceRequestResponse(
            status="success",
            request_id=request_id,
            message=f"Service request created successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating service request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/service-requests", tags=["Service"])
async def get_service_requests(username: str, password: str):
    """
    Get all service requests for a user
    """
    try:
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id, username FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id = user[0]
        
        # Get service requests
        db_manager.cursor.execute('''
            SELECT request_id, request_item, request_details, status, escalation_level, created_at
            FROM service_requests
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        requests = db_manager.cursor.fetchall()
        
        result = []
        for req in requests:
            result.append({
                'request_id': req[0],
                'request_item': req[1],
                'request_details': req[2],
                'status': req[3],
                'escalation_level': req[4],
                'created_at': req[5],
                'can_escalate': req[3] == 'pending'
            })
        
        return {
            "status": "success",
            "requests": result,
            "total": len(result)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching service requests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/service-request/{request_id}/escalate", response_model=EscalateServiceRequestResponse, tags=["Service"])
async def escalate_service_request(username: str, password: str, request_id: int):
    """
    Escalate a service request to next level
    Only works if request exists and hasn't been escalated beyond level 2
    
    Args:
        username: Username
        password: Password
        request_id: Request ID to escalate
        
    Returns:
        EscalateServiceRequestResponse with new escalation level
    """
    try:
        # Authenticate user
        db_manager.cursor.execute(
            'SELECT user_id FROM users WHERE username = ? AND password = ?',
            (username, password)
        )
        user = db_manager.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id = user[0]
        
        # Get request and verify ownership
        db_manager.cursor.execute(
            'SELECT request_id, escalation_level, status FROM service_requests WHERE request_id = ? AND user_id = ?',
            (request_id, user_id)
        )
        req = db_manager.cursor.fetchone()
        
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if req[2] != 'pending':
            raise HTTPException(status_code=400, detail="Only pending requests can be escalated")
        
        new_level = req[1] + 1
        
        if new_level > 3:
            raise HTTPException(status_code=400, detail="Request already escalated to maximum level")
        
        # Update escalation
        db_manager.cursor.execute('''
            UPDATE service_requests 
            SET escalation_level = ?, escalated_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
        ''', (new_level, request_id))
        
        db_manager.conn.commit()
        
        logger.info(f"Service request {request_id} escalated to level {new_level}")
        
        return EscalateServiceRequestResponse(
            status="success",
            request_id=request_id,
            escalation_level=new_level,
            message=f"Request escalated to level {new_level}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error escalating request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
