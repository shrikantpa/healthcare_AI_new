# Role-Based Guidance System - Implementation Guide

## Overview

A comprehensive role-specific disease outbreak guidance system has been implemented that provides tailored recommendations based on user roles (ASHA, DCMO, SCMO) and outbreak forecast data.

## Architecture

### Backend Components

#### 1. **New Endpoint: `/guidance` (POST)**

**Purpose**: Provides role-specific guidance for disease outbreak management

**Request**:
```json
{
  "username": "admin",
  "password": "admin123",
  "district": "Nashik",
  "state": "Maharashtra"
}
```

**Response**:
```json
{
  "status": "success",
  "username": "admin",
  "role": "ASHA",
  "district": "Nashik",
  "state": "Maharashtra",
  "forecast": {...},
  "guidance": {...},
  "message": "Role-specific guidance generated for ASHA"
}
```

#### 2. **Role-Specific Guidance Generation**

##### **ASHA (Accredited Social Health Activist)**
Focus: Community-level prevention and awareness
- **General Remedies**: Individual preventive measures, diet, sanitation
- **Social Remedies**: Community awareness camps, mass distribution initiatives
- **Government Regulatory Actions**: Medical camps, awareness sessions
- **Healthcare Body Actions**: Medicine stockpiling, testing kits, vaccination

##### **DCMO (District Chief Medical Officer)**
Focus: District-level resource management and healthcare arrangements
- **Cases Identified**: Total cases detected so far
- **Department Actions**: Healthcare team mobilization, testing centers
- **Inventory Arrangements**: Quantitative requirements for medicines, PPE, beds
- **Resource Deployment**: Doctor, nurse, paramedic allocation
- **Coordination Plan**: Inter-departmental coordination
- **Budget Allocation**: Estimated budget for response

##### **SCMO (State Chief Medical Officer)**
Focus: State-level strategic planning and emergency measures
- **State Overview**: Outbreak status across entire state
- **Highly Affected Districts**: Severity ranking of districts
- **Comparative Analysis**: Inter-district infection rate analysis
- **State-level Remedies**: State-wide initiatives
- **Medical Professional Deployment**: Army/paramedic deployment strategy
- **Emergency Measures**: Emergency protocols and mobilization
- **Inter-District Coordination**: Resource sharing strategy
- **Emergency Funding**: Fund sanctioning recommendations
- **Timeline & Milestones**: Implementation phases

### Frontend Components

#### 1. **New Page: `chat.html`**
ChatGPT-like interface for guidance generation
- Clean, modern design with sidebar and main chat area
- User information display with role badge
- Conversation history management
- Location selection prompt
- Real-time guidance display with formatted sections

#### 2. **New Module: `chat.js`**
JavaScript module handling:
- User authentication verification
- Location management
- Guidance fetching and display
- Role-specific guidance formatting
- Conversation history
- Message handling

## Data Flow

```
1. User Login
   ↓
2. Redirect to Chat Page (chat.html)
   ↓
3. Load User Info from localStorage
   ↓
4. Auto-load Initial Guidance OR Show Location Prompt
   ↓
5. Send POST /guidance request with user credentials + location
   ↓
6. Backend:
   a. Authenticate user
   b. Fetch forecast data (district or state-level based on role)
   c. Generate role-specific prompt for LLM
   d. Call Groq LLM with role-specific instructions
   e. Parse and return structured guidance
   ↓
7. Display role-specific guidance in chat interface
```

## Backend Implementation Details

### Helper Functions

#### `_get_forecast_for_guidance(district, state, role)`
- For ASHA/DCMO: Fetches single district forecast
- For SCMO: Fetches all districts in state for comparative analysis
- Returns structured forecast data

#### `_generate_role_specific_guidance(user_role, forecast_data, district, state)`
- Routes to role-specific guidance generator
- Calls appropriate function based on user role

#### `_generate_asha_guidance(forecast, district, state)`
- Creates LLM prompt focusing on community-level interventions
- Returns 4-component guidance (general, social, govt, healthcare)

#### `_generate_dcmo_guidance(forecast, district, state)`
- Creates LLM prompt focusing on resource management
- Returns district-level action plan with inventory details

#### `_generate_scmo_guidance(forecast, district, state)`
- Creates LLM prompt focusing on state-level strategy
- Returns comprehensive state-level outbreak response plan

## Frontend Implementation Details

### Key Functions

#### `initializeChat()`
- Verifies user session
- Loads user data from localStorage
- Updates sidebar with user info
- Triggers initial guidance load

#### `fetchRoleBasedGuidance()`
- Sends POST request to `/guidance` endpoint
- Handles authentication
- Displays loading indicator
- Processes response and displays guidance

#### `displayGuidance(guidanceData)`
- Main orchestrator for displaying guidance
- Shows forecast data
- Shows role-specific guidance sections

#### `displayRoleSpecificGuidance(role, guidance)`
- Routes to role-specific display function
- Formats and presents guidance in readable format

#### `addAssistantMessage(html)`
- Adds formatted message to chat interface
- Auto-scrolls to bottom
- Supports HTML content for rich formatting

## Login Flow Updates

1. **Login Page (index.html)**
   - User enters credentials
   - Authenticates against `/login` endpoint
   - Stores user data in localStorage
   - **Redirects to `chat.html`** (updated from `main.html`)

2. **Signup Page (signup.html)**
   - User fills registration form
   - Includes role selection (ASHA, DCMO, SCMO)
   - Creates account via `/signup` endpoint
   - Stores user data and location
   - **Auto-redirects to `chat.html`** with pre-filled location

## How to Use

### For ASHA Worker:
1. Login with ASHA credentials
2. Chat page loads with guidance for community prevention
3. See 4-part guidance (general, social, govt, healthcare remedies)
4. Can refresh guidance or change location

### For DCMO:
1. Login with DCMO credentials
2. Chat page shows district-level analysis
3. View inventory requirements, resource deployment plans
4. See high-level management strategy

### For SCMO:
1. Login with SCMO credentials
2. Chat page shows state-level overview
3. Compare all districts for infection rates
4. View emergency measures and deployment strategy
5. See inter-district coordination plans

## Example Requests

### ASHA Guidance Request:
```
POST /guidance
{
  "username": "asha_worker1",
  "password": "password",
  "district": "Nashik",
  "state": "Maharashtra"
}
```

### DCMO Guidance Request:
```
POST /guidance
{
  "username": "dcmo_nashik",
  "password": "password",
  "district": "Nashik",
  "state": "Maharashtra"
}
```

### SCMO Guidance Request:
```
POST /guidance
{
  "username": "scmo_maharashtra",
  "password": "password",
  "district": "Maharashtra",  // Can be any district in state
  "state": "Maharashtra"
}
```

## Key Features

✅ **Role-Based Customization**: Different guidance for different roles
✅ **ChatGPT-like Interface**: Modern, user-friendly chat interface
✅ **Forecast Integration**: Uses actual disease outbreak forecast data
✅ **LLM Integration**: Groq LLM generates contextual responses
✅ **Real-time Guidance**: Generates guidance on-demand
✅ **Conversation History**: Saves and displays past guidance requests
✅ **Location Management**: Dynamic location selection
✅ **Error Handling**: Comprehensive error handling and user feedback
✅ **Responsive Design**: Works on desktop and mobile devices

## Database Tables Used

1. **user_mapping**: For login (username, password, role)
2. **users**: For signup details (first_name, last_name, location, role)
3. **location**: District and state information
4. **malaria_state_data**: Historical outbreak data

## Files Created/Modified

### Created:
- `/frontend/chat.html` - Chat interface UI
- `/frontend/chat.js` - Chat interface logic

### Modified:
- `/backend/main.py` - Added `/guidance` endpoint and helper functions
- `/frontend/auth.js` - Updated redirects to chat.html

## Testing the Feature

### 1. Start Backend:
```bash
cd /workspaces/healthcare_AI_new/backend
python3 main.py
```

### 2. Start Frontend (separate terminal):
```bash
cd /workspaces/healthcare_AI_new/frontend
# Use any simple HTTP server or open index.html
```

### 3. Login Credentials:
- **Username**: admin
- **Password**: admin123
- **Role**: ASHA

### 4. Expected Flow:
1. Login page appears
2. Enter admin/admin123
3. Redirects to chat.html
4. Chat interface loads with user info
5. Auto-loads guidance for ASHA role
6. Displays role-specific guidance sections

## Notes

- Each role receives tailored guidance based on their responsibilities
- SCMO role gets state-level overview with district comparisons
- DCMO role gets district-level resource management guidance
- ASHA role gets community-level prevention guidance
- All guidance is generated using Groq LLM based on actual forecast data
- Guidance can be regenerated or location can be changed within chat interface

## Future Enhancements

1. **Message Persistence**: Save conversations to database
2. **Multi-District Analysis**: Compare multiple districts/states
3. **Export Guidance**: Download guidance as PDF/Report
4. **Real-time Alerts**: Push notifications for critical outbreaks
5. **Feedback System**: Rate guidance usefulness
6. **Audit Trail**: Track guidance requests and actions taken
