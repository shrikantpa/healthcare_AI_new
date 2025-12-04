# QUICK START - Role-Based Guidance System

## What Was Implemented?

A complete role-based guidance system that provides different disease outbreak management recommendations based on user roles: ASHA, DCMO, or SCMO.

## System Components

### 1. **New REST API Endpoint: `/guidance` (POST)**
   - Authenticates user
   - Fetches forecast data based on role
   - Generates role-specific guidance using LLM
   - Returns formatted guidance

### 2. **Chat Interface (chat.html)**
   - ChatGPT-like interface
   - Shows user info and role
   - Displays real-time guidance
   - Allows location changes
   - Conversation history

### 3. **Chat Logic (chat.js)**
   - Handles guidance requests
   - Formats role-specific guidance
   - Manages user sessions
   - Displays results

## Login Flow

```
Login (index.html)
    ↓
Verify Credentials
    ↓
Store User Data
    ↓
Redirect to chat.html
    ↓
Auto-load Role-Specific Guidance
```

## Role-Specific Guidance

### 🏥 ASHA (Health Worker)
**Focus**: Community-level prevention and awareness
- General remedies for individuals
- Social remedies for communities
- Government actions needed
- Healthcare facility actions

### 🏛️ DCMO (District Chief Medical Officer)
**Focus**: District resource management
- Cases identified
- Healthcare department actions
- Inventory arrangements
- Resource deployment strategy
- Coordination plans
- Budget allocation

### 🌍 SCMO (State Chief Medical Officer)
**Focus**: State-level strategic planning
- State-wide outbreak overview
- Comparison of all districts
- Identification of high-risk areas
- Emergency measures
- Medical professional deployment
- Inter-district coordination
- Emergency fund recommendations

## How It Works

1. **User Login**: Enters credentials on index.html
2. **Authentication**: Backend verifies against user_mapping table
3. **Redirect**: User sent to chat.html
4. **Location Selection**: Shows district/state if available from signup
5. **Forecast Fetch**: System retrieves outbreak data for location
6. **LLM Generation**: Based on role, creates specific prompt for Groq LLM
7. **Guidance Display**: Formatted guidance shown in chat interface
8. **Conversation History**: Previous requests available in sidebar

## API Endpoint Details

### POST /guidance

**Request Body**:
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
  "forecast": {
    "outbreak_status": "high_risk",
    "disease_name": "Malaria",
    "total_expected_cases": 150,
    ...
  },
  "guidance": {
    "general_remedies": "...",
    "social_remedies": "...",
    "govt_regulatory_actions": "...",
    "healthcare_body_actions": "..."
  },
  "message": "Role-specific guidance generated for ASHA"
}
```

## Testing Instructions

### Step 1: Start Backend Server
```bash
cd backend
python3 main.py
```
The API will run on `http://localhost:8000`

### Step 2: Open Frontend
- Open `frontend/index.html` in a web browser
- Or set up a simple HTTP server: `python3 -m http.server 5000`

### Step 3: Login
- **Username**: admin
- **Password**: admin123

### Step 4: Experience Chat Interface
- Chat interface loads automatically
- Shows user: admin, Role: ASHA
- Auto-loads initial guidance for Nashik district
- Shows all 4 guidance sections for ASHA

### Step 5: Try Different Features
- Change location in chat
- Reload guidance
- Check conversation history in sidebar
- View role-specific guidance formatting

## File Structure

```
frontend/
├── index.html           (Login page)
├── signup.html          (Registration with role selection)
├── chat.html            (NEW - Chat interface)
├── auth.js              (Updated - redirects to chat.html)
├── chat.js              (NEW - Chat logic)
└── styles.css           (Chat styles included in chat.html)

backend/
├── main.py              (Updated - Added /guidance endpoint + helpers)
├── database.py          (Existing - No changes)
├── llm_service.py       (Existing - No changes)
└── reinitialize_db.py   (Existing - For DB reset)
```

## Key Features Implemented

✅ **Authentication**: User login verification via user_mapping table
✅ **Role Detection**: Automatically detects user role
✅ **Forecast Integration**: Fetches real outbreak data
✅ **Role-Specific Prompts**: Different prompts based on role
✅ **LLM Processing**: Groq LLM generates contextual guidance
✅ **Chat Interface**: Modern, user-friendly interface
✅ **Responsive Design**: Works on mobile and desktop
✅ **Error Handling**: Comprehensive error messages
✅ **Session Management**: Stores user data locally
✅ **Conversation History**: Saves past requests

## Default Test User

After running `reinitialize_db.py`:
- **Username**: admin
- **Password**: admin123
- **Role**: ASHA

## Troubleshooting

### Backend Not Running?
- Check if port 8000 is available
- Run: `python3 backend/main.py`
- Should see: "Uvicorn running on http://0.0.0.0:8000"

### Chat Not Loading?
- Verify backend is running
- Check browser console (F12) for errors
- Ensure user is logged in (check localStorage)

### No Guidance Appearing?
- Check district/state are selected
- Verify location data exists in database
- Check browser console for API errors

### "No outbreak data" Message?
- Select a valid district/state combination
- Check that malaria_data.json was loaded
- Verify data in database: SELECT COUNT(*) FROM malaria_state_data;

## Next Steps

1. **Test with Different Roles**: Create DCMO and SCMO users for testing
2. **Verify LLM Integration**: Check Groq API is working
3. **Test All Locations**: Try different districts and states
4. **Check Guidance Quality**: Review generated guidance for accuracy
5. **Mobile Testing**: Test on mobile devices

## Support

For issues or questions:
1. Check browser console (F12) for JavaScript errors
2. Check terminal where backend is running for Python errors
3. Verify database has data: `sqlite3 malaria_data.db "SELECT COUNT(*) FROM malaria_state_data;"`
4. Check API is responding: `curl http://localhost:8000/health`

---

**Status**: ✅ Implementation Complete
**Date**: December 4, 2025
