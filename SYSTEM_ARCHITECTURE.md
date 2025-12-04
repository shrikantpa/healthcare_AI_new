# System Architecture Diagram

## Overall Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER LOGIN (index.html)                       │
│                                                                   │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │ Enter Credentials   │         │ Username: admin      │       │
│  │ Username            │─────┬──▶│ Password: admin123   │       │
│  │ Password            │     │   │ Role: ASHA           │       │
│  └─────────────────────┘     │   └──────────────────────┘       │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               │ Verify against
                               │ user_mapping table
                               ↓
                    ┌────────────────────┐
                    │  /login endpoint   │
                    │  Backend Auth      │
                    └────────────────────┘
                               │
                    ✓ Success  │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CHAT INTERFACE (chat.html)                      │
│                                                                   │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │    SIDEBAR       │  │       MAIN CHAT AREA              │  │
│  │                  │  │                                    │  │
│  │ User: admin      │  │  Welcome to Aayura                │  │
│  │ Role: ASHA       │  │  Disease Outbreak Guidance        │  │
│  │ Location:        │  │                                    │  │
│  │ Nashik, MH       │  │  [Loading guidance...]             │  │
│  │                  │  │                                    │  │
│  │ ➕ New Guidance  │  │  📊 Outbreak Forecast Data         │  │
│  │                  │  │  Status: High Risk                │  │
│  │ Conversations:   │  │  Expected Cases: 150              │  │
│  │ • ASHA-Nashik    │  │                                    │  │
│  │                  │  │  ✅ Role-Specific Guidance        │  │
│  │ 🔓 Logout        │  │                                    │  │
│  └──────────────────┘  │  🏥 General Remedies              │  │
│                        │  [Guidance content...]             │  │
│                        │                                    │  │
│                        │  👥 Social Remedies                │  │
│                        │  [Guidance content...]             │  │
│                        │                                    │  │
│                        │  🏛️ Government Actions            │  │
│                        │  [Guidance content...]             │  │
│                        │                                    │  │
│                        │  🩺 Healthcare Actions             │  │
│                        │  [Guidance content...]             │  │
│                        └────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [Type message or ask for guidance...]   [📤 Send]      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ Fetch Guidance (POST /guidance)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (main.py)                              │
│                                                                   │
│  1. Authenticate User                                            │
│     └─▶ Query user_mapping table                               │
│                                                                   │
│  2. Fetch Forecast Data                                          │
│     ├─ ASHA/DCMO: Single district forecast                     │
│     └─ SCMO: All districts in state                            │
│                                                                   │
│  3. Check User Role                                              │
│     ├─ If ASHA: _generate_asha_guidance()                      │
│     ├─ If DCMO: _generate_dcmo_guidance()                      │
│     └─ If SCMO: _generate_scmo_guidance()                      │
│                                                                   │
│  4. Generate LLM Prompt (Role-Specific)                          │
│     └─▶ Format prompt based on role                            │
│                                                                   │
│  5. Call Groq LLM                                                │
│     └─▶ Generate contextual guidance                           │
│                                                                   │
│  6. Parse LLM Response                                           │
│     └─▶ Extract JSON guidance                                  │
│                                                                   │
│  7. Return to Frontend                                           │
│     └─▶ RoleBasedGuidanceResponse                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ Display Guidance
                               ↓
         ┌──────────────────────────────────────────┐
         │  Format and Display in Chat Interface    │
         │  Role-Specific Sections                  │
         │  Forecast Data                           │
         │  Conversation History                    │
         └──────────────────────────────────────────┘
```

## Role-Specific Guidance Flow

### ASHA (Health Worker)
```
User (ASHA)
    │
    ├─▶ POST /guidance
    │   ├─ Username: asha_worker1
    │   ├─ Role: ASHA (from auth)
    │   └─ Location: District, State
    │
    ├─▶ Backend Processing
    │   ├─ Get single district forecast
    │   ├─ Create ASHA prompt:
    │   │  ├─ General Remedies (individual prevention)
    │   │  ├─ Social Remedies (community-level)
    │   │  ├─ Government Actions (awareness, camps)
    │   │  └─ Healthcare Actions (stockpiling, vaccines)
    │   ├─ Call Groq LLM
    │   └─ Parse response
    │
    └─▶ Display 4-Section Guidance
        ├─ 🏥 General Remedies
        ├─ 👥 Social Remedies
        ├─ 🏛️ Government Actions
        └─ 🩺 Healthcare Actions
```

### DCMO (District Chief Medical Officer)
```
User (DCMO)
    │
    ├─▶ POST /guidance
    │   ├─ Username: dcmo_district
    │   ├─ Role: DCMO (from auth)
    │   └─ Location: District, State
    │
    ├─▶ Backend Processing
    │   ├─ Get single district forecast
    │   ├─ Create DCMO prompt:
    │   │  ├─ Cases Identified (total count)
    │   │  ├─ Department Actions (healthcare mobilization)
    │   │  ├─ Inventory Arrangements (quantitative)
    │   │  ├─ Resource Deployment (doctors, nurses, paramedics)
    │   │  ├─ Coordination Plan (inter-departmental)
    │   │  └─ Budget Allocation (estimated costs)
    │   ├─ Call Groq LLM
    │   └─ Parse response
    │
    └─▶ Display 6-Section Guidance
        ├─ 📊 Cases Identified
        ├─ 🏥 Department Actions
        ├─ 📦 Inventory Arrangements
        ├─ 👨‍⚕️ Resource Deployment
        ├─ 🤝 Coordination Plan
        └─ 💰 Budget Allocation
```

### SCMO (State Chief Medical Officer)
```
User (SCMO)
    │
    ├─▶ POST /guidance
    │   ├─ Username: scmo_state
    │   ├─ Role: SCMO (from auth)
    │   └─ Location: Any District, State
    │
    ├─▶ Backend Processing
    │   ├─ Get ALL districts in state (comparative)
    │   ├─ Create SCMO prompt:
    │   │  ├─ State Overview (all districts)
    │   │  ├─ Highly Affected Districts (ranking)
    │   │  ├─ Comparative Analysis (district comparison)
    │   │  ├─ State-level Remedies (state-wide initiatives)
    │   │  ├─ Medical Professional Deployment (army, paramedics)
    │   │  ├─ Emergency Measures (protocols, mobilization)
    │   │  ├─ Inter-District Coordination (resource sharing)
    │   │  ├─ Emergency Funding (sanctioning recommendations)
    │   │  └─ Timeline & Milestones (phased implementation)
    │   ├─ Call Groq LLM
    │   └─ Parse response
    │
    └─▶ Display 9-Section Guidance
        ├─ 🌍 State Overview
        ├─ 🔴 Highly Affected Districts
        ├─ 📈 Comparative Analysis
        ├─ 💊 State-level Remedies
        ├─ 👨‍⚕️ Medical Professional Deployment
        ├─ ⚠️ Emergency Measures
        ├─ 🔗 Inter-District Coordination
        ├─ 💰 Emergency Funding
        └─ 📅 Timeline & Milestones
```

## Database Schema Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                      SQLITE DATABASE                             │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  user_mapping    │  │     users        │  │   location   │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤  │
│  │ user_id (PK)     │  │ user_id (PK)     │  │ location_id  │  │
│  │ username (UNIQ)  │  │ first_name       │  │ state        │  │
│  │ password         │  │ last_name        │  │ district     │  │
│  │ role             │  │ username (UNIQ)  │  └──────────────┘  │
│  │                  │  │ password         │                    │
│  │ Sample:          │  │ district         │  ┌────────────────┐ │
│  │ admin            │  │ state            │  │ malaria_state  │ │
│  │ admin123         │  │ location_id (FK) │  │ _data          │ │
│  │ ASHA             │  │ role             │  ├────────────────┤ │
│  │                  │  │ created_at       │  │ record_id (PK) │ │
│  │                  │  │                  │  │ location_id(FK)│ │
│  │                  │  │ Sample:          │  │ year           │ │
│  │                  │  │ user1            │  │ cases_examined │ │
│  │                  │  │ John             │  │ cases_detected │ │
│  │                  │  │ Doe              │  │ male_detected  │ │
│  │                  │  │ username1        │  │ female_detected│ │
│  │                  │  │ pwd              │  └────────────────┘ │
│  │                  │  │ Nashik           │                    │
│  │                  │  │ Maharashtra      │                    │
│  │                  │  │ 1                │                    │
│  │                  │  │ ASHA             │                    │
│  │                  │  │ 2025-12-04       │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                   │
│  Data Flow:                                                       │
│  1. /login → Query user_mapping by username+password             │
│  2. /guidance → Get role from user_mapping                       │
│  3. Fetch forecast → Query malaria_state_data by location_id     │
│  4. User profile → Query users by username (for location info)   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## API Request/Response Flow

```
Client (Frontend)                 Backend API
     │                                 │
     ├─ POST /guidance ────────────────▶│
     │  {                               │
     │    "username": "admin",          │
     │    "password": "admin123",       │
     │    "district": "Nashik",         │
     │    "state": "Maharashtra"        │
     │  }                               │
     │                                  │
     │   Step 1: Authenticate          │
     │   ├─ Query user_mapping         │
     │   └─ Get role: ASHA             │
     │                                  │
     │   Step 2: Fetch Forecast        │
     │   ├─ Query location table       │
     │   ├─ Query malaria_state_data   │
     │   └─ Get forecast data          │
     │                                  │
     │   Step 3: Generate Prompt       │
     │   └─ ASHA-specific prompt       │
     │                                  │
     │   Step 4: Call Groq LLM         │
     │   └─ Get guidance               │
     │                                  │
     │   Step 5: Parse Response        │
     │   └─ Extract JSON               │
     │                                  │
     │◀─────────────────────────────────┤
     │  200 OK                          │
     │  {                               │
     │    "status": "success",          │
     │    "role": "ASHA",               │
     │    "forecast": {...},            │
     │    "guidance": {                 │
     │      "general_remedies": "...",  │
     │      "social_remedies": "...",   │
     │      ...                         │
     │    }                             │
     │  }                               │
     │                                  │
     ├─ Display in Chat UI             │
     │                                  │
```

---

**Diagram Legend**:
- ▶ = Data Flow
- PK = Primary Key
- FK = Foreign Key
- UNIQ = Unique Constraint
- ✓ = Success
- ASHA = Accredited Social Health Activist
- DCMO = District Chief Medical Officer
- SCMO = State Chief Medical Officer
