# Action Plan Endpoint Documentation

## Overview
The `/action-plan` endpoint provides role-based recommendations for malaria outbreak management. It automatically fetches forecast data and generates LLM-based action plans tailored to the user's role.

## Endpoint Details

**URL:** `POST /action-plan`

**Base URL:** `http://localhost:8000`

## Request Body

```json
{
  "username": "string (required)",
  "district": "string (optional)",
  "state": "string (optional)"
}
```

### Parameters

- **username** (required): The username of the user requesting the action plan
- **district** (optional): Specific district name. If not provided, uses user's registered district
- **state** (optional): Specific state name. If not provided, uses user's registered state

## Response

```json
{
  "status": "success",
  "role": "string",
  "district": "string",
  "state": "string",
  "forecast_data": { ... },
  "action_plan": { ... },
  "message": "string"
}
```

## How It Works

### Step 1: User Identification
- Fetches user details from database using username
- Identifies user's role: **ASHA**, **DCMO**, or **SCMO**
- Retrieves user's assigned district and state (can be overridden in request)

### Step 2: Forecast Retrieval
- Queries malaria data from `malaria_state_data` table
- Calls LLM to generate outbreak forecast
- Returns forecast with status, statistics, and LLM analysis

### Step 3: Role-Based Action Plan Generation
Based on the role, generates specific recommendations:

## Role-Specific Action Plans

### 1. ASHA (Accredited Social Health Activist)

**Focus:** Community-level health awareness and preventive measures

**Action Plan Includes:**

a) **General Remedies**
   - Personal health measures to prevent infection
   - Daily preventive practices
   - Immune-boosting foods and natural remedies
   - Water and sanitation practices

b) **Social Remedies**
   - Mass awareness campaigns
   - Community-level interventions
   - Educational sessions for schools
   - Door-to-door health awareness
   - Community engagement strategies

c) **Government Regulatory Body Actions**
   - Government health campaigns
   - Vaccination drives and health camps
   - Educational programs
   - Public health advisories

d) **Healthcare Body Actions**
   - Essential medicines availability
   - Testing kits availability
   - Hospital bed information
   - Healthcare staff availability
   - Vaccination schedules
   - Monitoring activities

### 2. DCMO (District Chief Medical Officer)

**Focus:** District-level inventory management and healthcare coordination

**Action Plan Includes:**

a) **Cases Identified**
   - Total cases identified
   - Severity distribution
   - Age and gender breakdown
   - Mortality rate

b) **Healthcare Department Actions Taken**
   - Diagnostic testing mobilized
   - Treatment protocols implemented
   - Isolation measures
   - Staff deployment
   - Inter-departmental coordination

c) **High-Level Inventory Arrangements**
   - Hospital beds required
   - ICU beds and ventilators
   - Antimalarial medicines inventory
   - Diagnostic kits and equipment
   - PPE for healthcare workers
   - Staffing requirements
   - Blood bank arrangements
   - Oxygen cylinder requirements

d) **Resource Management & Emergency Measures**
   - Budget allocation
   - Supply chain management
   - Inter-district coordination
   - Staff training programs
   - Equipment procurement timeline

e) **Surveillance & Monitoring**
   - Real-time case tracking
   - Data reporting mechanisms
   - Response time improvements

### 3. SCMO (State Chief Medical Officer)

**Focus:** State-level overview and strategic resource allocation

**Action Plan Includes:**

a) **State-Level Overview**
   - Total cases across state
   - Number of severely affected districts
   - Comparative analysis
   - Overall mortality rate
   - Trend analysis

b) **District-Wise Analysis**
   - Infection severity levels by district
   - Case count by district
   - Healthcare infrastructure status
   - Resource gaps identification
   - Intervention priority

c) **Highly Infected Districts**
   - Identification of severely affected districts
   - Critical resource shortages
   - Healthcare capacity assessment
   - Support requirements

d) **Resource Allocation & Deployment**
   - Paramedical professionals deployment
   - Army doctors deployment for critical areas
   - Central government support requests
   - Inter-district resource sharing
   - Medical equipment redistribution

e) **Emergency Funding & Financial Measures**
   - Emergency funds allocation
   - Budget breakdown by district
   - Central assistance requests
   - Procurement fast-tracking
   - Insurance and compensation schemes

f) **State-Level Initiatives**
   - Mass vaccination campaigns
   - Telemedicine services
   - Research and surveillance programs
   - Inter-state coordination
   - Media and public communication
   - Disaster management protocols

g) **Timeline & Milestones**
   - Immediate actions (1-7 days)
   - Short-term measures (1-4 weeks)
   - Medium-term strategies (1-3 months)
   - Long-term preparedness (3-12 months)

## Example Requests

### ASHA Worker
```bash
curl -X POST http://localhost:8000/action-plan \
  -H "Content-Type: application/json" \
  -d '{
    "username": "asha_worker1",
    "district": "Pune",
    "state": "Maharashtra"
  }'
```

### DCMO Officer
```bash
curl -X POST http://localhost:8000/action-plan \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dcmo_officer",
    "district": "Mumbai"
  }'
```

### SCMO Officer
```bash
curl -X POST http://localhost:8000/action-plan \
  -H "Content-Type: application/json" \
  -d '{
    "username": "scmo_state",
    "state": "Maharashtra"
  }'
```

## Example Response

```json
{
  "status": "success",
  "role": "ASHA",
  "district": "Pune",
  "state": "Maharashtra",
  "forecast_data": {
    "status": "outbreak_detected",
    "district": "Pune",
    "forecast": {
      "outbreak_status": "high_risk",
      "disease_name": "Malaria",
      "total_expected_cases": 250,
      "forecast_by_gender": {
        "male": 150,
        "female": 100
      }
    }
  },
  "action_plan": {
    "role": "ASHA",
    "general_remedies": "Use mosquito nets, clean water storage, proper sanitation...",
    "social_remedies": "Conduct awareness camps, door-to-door campaigns...",
    "govt_actions": "Vaccination drives, public health advisories...",
    "healthcare_actions": "Ensure medicine availability, testing kits, hospital beds...",
    "full_plan": "Comprehensive action plan from LLM..."
  },
  "message": "Action plan generated for ASHA user in Pune, Maharashtra"
}
```

## Error Responses

### User Not Found
```json
{
  "detail": "User not found",
  "status": "error"
}
```

### Server Error
```json
{
  "detail": "Error generating action plan: [error details]",
  "status": "error"
}
```

## Authentication

Currently, the endpoint uses the `username` parameter for user identification. Consider adding JWT token authentication for production use.

## Database Requirements

The endpoint requires:
- `users` table with: user_id, username, role, district, state
- `user_mapping` table with: user_id, username, role (for default users)
- `malaria_state_data` table with outbreak data by district

## LLM Integration

- **Service:** Groq API
- **Model:** llama-3.3-70b-versatile
- **Temperature:** 0 (deterministic responses)

The action plan is generated using the Groq LLM with prompts specifically tailored to each role's responsibilities and focus areas.

## Notes

1. **Performance:** LLM API calls may take 5-10 seconds to complete
2. **Forecast Data:** Action plans are based on available malaria data in the database
3. **Customization:** Prompts can be modified in the helper functions to match local requirements
4. **Caching:** Consider implementing caching for frequently requested action plans
5. **Logging:** All requests and responses are logged for audit trail

## Future Enhancements

- [ ] Add JWT authentication
- [ ] Implement response caching
- [ ] Add multi-language support
- [ ] Add export to PDF functionality
- [ ] Add real-time updates for forecast data
- [ ] Add historical comparison of action plans
- [ ] Implement email notifications for critical plans
