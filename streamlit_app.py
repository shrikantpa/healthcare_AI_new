"""
Streamlit UI for Healthcare AI Malaria Outbreak Forecasting System
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Aayura - Malaria Outbreak Forecasting",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 80vh;
    }
    .message-user {
        background-color: #667eea;
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        margin-left: auto;
        max-width: 70%;
        word-wrap: break-word;
    }
    .message-assistant {
        background-color: #f0f0f0;
        color: #333;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        margin-right: auto;
        max-width: 70%;
        word-wrap: break-word;
    }
    .message-system {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        text-align: center;
    }
    .user-info {
        background-color: #f7f7f7;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .guidance-card {
        background-color: #f9f9f9;
        padding: 1rem;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .forecast-section {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-low-risk {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .status-medium-risk {
        background-color: #fff9c4;
        color: #f57f17;
    }
    .status-high-risk {
        background-color: #ffccbc;
        color: #d84315;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user' not in st.session_state:
    st.session_state.user = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_password' not in st.session_state:
    st.session_state.user_password = None

def login_user(username, password):
    """Login user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            st.session_state.user = user_data
            st.session_state.user_password = password
            st.session_state.page = 'chat'
            return True, "Login successful!"
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def signup_user(first_name, last_name, username, password, district, state, role):
    """Signup user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/signup",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "district": district,
                "state": state,
                "role": role
            },
            timeout=10
        )
        if response.status_code == 200:
            return True, "Signup successful! Please login with your credentials."
        else:
            error_detail = response.json().get('detail', 'Signup failed')
            return False, f"Signup error: {error_detail}"
    except Exception as e:
        return False, f"Signup error: {str(e)}"

def get_locations():
    """Get available locations"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/locations",
            timeout=10
        )
        if response.status_code == 200:
            locations = response.json()
            states = list(set([loc['state'] for loc in locations]))
            return sorted(states), locations
        else:
            return [], []
    except Exception as e:
        st.error(f"Error fetching locations: {str(e)}")
        return [], []

def get_districts_for_state(state, locations):
    """Get districts for a state"""
    return sorted(list(set([loc['district'] for loc in locations if loc['state'] == state])))

def fetch_guidance():
    """Fetch role-based guidance"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/guidance",
            json={
                "username": st.session_state.user['username'],
                "password": st.session_state.user_password,
                "district": st.session_state.user['district'],
                "state": st.session_state.user['state']
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching guidance: {str(e)}")
        return None

def render_guidance(guidance_data):
    """Render guidance data"""
    if not guidance_data or guidance_data.get('status') != 'success':
        st.warning("Could not fetch guidance data")
        return
    
    # Display forecast
    if guidance_data.get('forecast'):
        forecast = guidance_data['forecast']
        st.markdown("### 📊 Outbreak Forecast")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            outbreak_status = forecast.get('outbreak_status', 'low_risk').replace('_', ' ').title()
            status_class = f"status-{forecast.get('outbreak_status', 'low_risk').replace('_', '-')}"
            st.metric("Outbreak Status", outbreak_status)
        
        with col2:
            st.metric("Expected Cases", forecast.get('total_expected_cases', 0))
        
        with col3:
            st.metric("Male Cases", forecast.get('forecast_by_gender', {}).get('male', 0))
        
        with col4:
            st.metric("Female Cases", forecast.get('forecast_by_gender', {}).get('female', 0))
        
        st.markdown(f"**Disease:** {forecast.get('disease_name', 'Malaria')}")
        st.markdown(f"**Confidence Level:** {forecast.get('confidence_level', 0)}%")
    
    # Display role-specific guidance
    role = guidance_data.get('role', '')
    guidance = guidance_data.get('guidance', {})
    
    st.markdown("### ✅ Role-Specific Guidance")
    
    if role == 'ASHA':
        st.markdown("#### 🏥 General Remedies")
        st.info(guidance.get('general_remedies', 'No data available'))
        
        st.markdown("#### 👥 Social Remedies")
        st.info(guidance.get('social_remedies', 'No data available'))
        
        st.markdown("#### 🏛️ Government Regulatory Actions")
        st.warning(guidance.get('govt_regulatory_actions', 'No data available'))
        
        st.markdown("#### 🩺 Healthcare Body Actions")
        st.success(guidance.get('healthcare_body_actions', 'No data available'))
    
    elif role == 'DCMO':
        st.markdown("#### 📊 Cases Identified")
        st.info(f"{guidance.get('cases_identified', 0)} cases identified")
        
        st.markdown("#### 🏥 Department Actions")
        st.info(guidance.get('department_actions', 'No data available'))
        
        st.markdown("#### 📦 Inventory Arrangements")
        st.warning(guidance.get('inventory_arrangements', 'No data available'))
        
        st.markdown("#### 👨‍⚕️ Resource Deployment")
        st.info(guidance.get('resource_deployment', 'No data available'))
        
        st.markdown("#### 🤝 Coordination Plan")
        st.success(guidance.get('coordination_plan', 'No data available'))
        
        st.markdown("#### 💰 Budget Allocation")
        st.warning(guidance.get('budget_allocation', 'No data available'))
    
    elif role == 'SCMO':
        st.markdown("#### 🌍 State Overview")
        st.info(guidance.get('state_overview', 'No data available'))
        
        st.markdown("#### 🔴 Highly Affected Districts")
        st.warning(guidance.get('highly_affected_districts', 'No data available'))
        
        st.markdown("#### 📈 Comparative Analysis")
        st.info(guidance.get('comparative_analysis', 'No data available'))
        
        st.markdown("#### 💊 State-level Remedies")
        st.success(guidance.get('state_level_remedies', 'No data available'))
        
        st.markdown("#### 👨‍⚕️ Medical Professional Deployment")
        st.warning(guidance.get('medical_professional_deployment', 'No data available'))
        
        st.markdown("#### ⚠️ Emergency Measures")
        st.error(guidance.get('emergency_measures', 'No data available'))
        
        st.markdown("#### 🔗 Inter-District Coordination")
        st.info(guidance.get('inter_district_coordination', 'No data available'))
        
        st.markdown("#### 💰 Emergency Funding")
        st.warning(guidance.get('emergency_funding', 'No data available'))
        
        st.markdown("#### 📅 Timeline & Milestones")
        st.success(guidance.get('timeline_and_milestones', 'No data available'))

def login_page():
    """Login page"""
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🏥 Aayura</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #764ba2;'>Malaria Outbreak Forecasting System</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter username and password")
        
        st.markdown("---")
        if st.button("Go to Signup", use_container_width=True):
            st.session_state.page = 'signup'
            st.rerun()

def signup_page():
    """Signup page"""
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🏥 Aayura</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #764ba2;'>Create Account</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign Up")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            first_name = st.text_input("First Name")
        
        with col_b:
            last_name = st.text_input("Last Name")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        states, locations = get_locations()
        
        if states:
            state = st.selectbox("State", states)
            districts = get_districts_for_state(state, locations)
            district = st.selectbox("District", districts if districts else ["Select a state first"])
        else:
            st.error("Could not load locations. Please try again later.")
            state = ""
            district = ""
        
        role = st.selectbox("Role", ["ASHA", "DCMO", "SCMO"])
        
        if st.button("Sign Up", use_container_width=True):
            if not all([first_name, last_name, username, password, confirm_password, state, district]):
                st.warning("Please fill all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = signup_user(first_name, last_name, username, password, district, state, role)
                if success:
                    st.success(message)
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("---")
        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def chat_page():
    """Chat page"""
    # Header
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🏥 Aayura Chat Interface</h1>", unsafe_allow_html=True)
    
    # User Info Sidebar
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        user = st.session_state.user
        st.markdown(f"### 👤 {user['first_name']} {user['last_name']}")
        st.markdown(f"**Username:** {user['username']}")
        st.markdown(f"**Role:** {user['role']}")
        st.markdown(f"**Location:** 📍 {user['district']}, {user['state']}")
    
    with col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_password = None
            st.session_state.chat_history = []
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("---")
    
    # Load initial guidance if chat is empty
    if not st.session_state.chat_history:
        with st.spinner("Loading default guidance..."):
            guidance_data = fetch_guidance()
            if guidance_data:
                st.session_state.chat_history.append({
                    'type': 'system',
                    'content': f"Welcome {user['first_name']}! Here is your role-specific guidance for {user['district']}, {user['state']}.",
                    'timestamp': datetime.now()
                })
                st.session_state.chat_history.append({
                    'type': 'guidance',
                    'content': guidance_data,
                    'timestamp': datetime.now()
                })
    
    # Chat display area
    st.markdown("### 💬 Chat History")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['type'] == 'system':
                st.info(message['content'])
            elif message['type'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            elif message['type'] == 'guidance':
                render_guidance(message['content'])
            elif message['type'] == 'assistant':
                st.info(message['content'])
    
    st.markdown("---")
    
    # Message input
    st.markdown("### Send Message")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_message = st.text_input("Type your message here...", key="message_input")
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    if send_button and user_message:
        # Add user message
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_message,
            'timestamp': datetime.now()
        })
        
        # Check message keywords
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ['guidance', 'reload', 'remedy', 'remedies', 'action', 'what', 'suggest', 'implement']):
            # Fetch and display guidance
            with st.spinner("Fetching guidance..."):
                guidance_data = fetch_guidance()
                if guidance_data:
                    st.session_state.chat_history.append({
                        'type': 'guidance',
                        'content': guidance_data,
                        'timestamp': datetime.now()
                    })
                else:
                    st.session_state.chat_history.append({
                        'type': 'assistant',
                        'content': "Could not fetch guidance. Please try again.",
                        'timestamp': datetime.now()
                    })
        else:
            # Default assistant response
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': f"I'm here to help with outbreak guidance based on your role. Try asking for 'guidance', 'remedies', 'actions', or ask me to 'reload' for the latest information.",
                'timestamp': datetime.now()
            })
        
        st.rerun()

# Main app logic
if st.session_state.user is None:
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()
else:
    chat_page()
