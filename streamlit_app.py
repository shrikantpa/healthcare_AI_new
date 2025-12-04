"""
Streamlit UI for Healthcare AI Malaria Outbreak Forecasting System
Dynamic, Interactive, and User-Friendly
"""
import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="🏥 Aayura - Disease Outbreak Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS with animations and modern styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        padding: 0;
    }
    
    /* Header Styling */
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
    }
    
    .header-main h1 {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-main p {
        font-size: 16px;
        opacity: 0.95;
    }
    
    /* User Info Card */
    .user-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .user-info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }
    
    .info-item {
        background: white;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .info-label {
        font-size: 12px;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .info-value {
        font-size: 16px;
        color: #333;
        font-weight: 700;
    }
    
    /* Chat Container */
    .chat-message {
        margin-bottom: 15px;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin-left: 40px;
        text-align: right;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .message-assistant {
        background: #f0f4f8;
        color: #333;
        padding: 15px;
        border-radius: 12px;
        margin-right: 40px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .message-system {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1565c0;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(21, 101, 192, 0.15);
    }
    
    /* Forecast Card */
    .forecast-card {
        background: linear-gradient(135deg, #fff5e6 0%, #ffe0b2 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #ff9800;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
    }
    
    /* Guidance Section */
    .guidance-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
    }
    
    .guidance-title {
        font-size: 18px;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .guidance-content {
        font-size: 14px;
        line-height: 1.8;
        color: #555;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        margin: 5px 0;
    }
    
    .status-low {
        background: #c8e6c9;
        color: #2e7d32;
    }
    
    .status-medium {
        background: #fff9c4;
        color: #f57f17;
    }
    
    .status-high {
        background: #ffccbc;
        color: #d84315;
    }
    
    /* Input Area */
    .input-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Loading Animation */
    .loading {
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 12px;
        opacity: 0.9;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# API Functions
def login_api(username, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, f"Error: {str(e)}"

def signup_api(first_name, last_name, username, password, district, state, role):
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
            return True, "Signup successful! Please login."
        else:
            return False, response.json().get('detail', 'Signup failed')
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_locations_api():
    try:
        response = requests.get(f"{API_BASE_URL}/locations", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_guidance_api(username, password, district, state):
    try:
        response = requests.post(
            f"{API_BASE_URL}/guidance",
            json={
                "username": username,
                "password": password,
                "district": district,
                "state": state
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_role_emoji(role):
    emojis = {
        "ASHA": "👩‍⚕️",
        "DCMO": "👨‍💼",
        "SCMO": "🎖️"
    }
    return emojis.get(role, "👤")

def get_status_class(status):
    if "low" in status.lower():
        return "status-low"
    elif "medium" in status.lower():
        return "status-medium"
    else:
        return "status-high"

def format_forecast(forecast):
    if not forecast:
        return None
    
    html = f"""
    <div class="forecast-card">
        <div style="font-weight: 700; font-size: 18px; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
            📊 Malaria Outbreak Forecast
            <span class="status-badge {get_status_class(forecast.get('outbreak_status', 'low'))}">
                {forecast.get('outbreak_status', 'Low Risk').replace('_', ' ').title()}
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px;">
            <div><strong>Disease:</strong> {forecast.get('disease_name', 'Malaria')}</div>
            <div><strong>Expected Cases:</strong> {forecast.get('total_expected_cases', 0)}</div>
            <div><strong>Male Cases:</strong> {forecast.get('forecast_by_gender', {}).get('male', 0)}</div>
            <div><strong>Female Cases:</strong> {forecast.get('forecast_by_gender', {}).get('female', 0)}</div>
            <div><strong>Age 0-5:</strong> {forecast.get('forecast_by_age_group', {}).get('children_0_5', 0)}</div>
            <div><strong>Age 5-18:</strong> {forecast.get('forecast_by_age_group', {}).get('youth_5_18', 0)}</div>
            <div><strong>Age 18-60:</strong> {forecast.get('forecast_by_age_group', {}).get('adults_18_60', 0)}</div>
            <div><strong>Age 60+:</strong> {forecast.get('forecast_by_age_group', {}).get('elderly_60_plus', 0)}</div>
        </div>
        <div><strong>Confidence Level:</strong> {forecast.get('confidence_level', 0)}%</div>
        <div style="margin-top: 15px; padding: 12px; background: white; border-radius: 8px; font-style: italic;">
            💡 {forecast.get('recommendations', 'Continue preventive measures.')}
        </div>
    </div>
    """
    return html

def format_guidance_asha(guidance):
    return f"""
    <div class="guidance-section">
        <div class="guidance-title">🏥 General Remedies</div>
        <div class="guidance-content">{guidance.get('general_remedies', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">👥 Social Remedies</div>
        <div class="guidance-content">{guidance.get('social_remedies', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🏛️ Government Actions</div>
        <div class="guidance-content">{guidance.get('govt_regulatory_actions', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🩺 Healthcare Actions</div>
        <div class="guidance-content">{guidance.get('healthcare_body_actions', 'N/A')}</div>
    </div>
    """

def format_guidance_dcmo(guidance):
    return f"""
    <div class="guidance-section">
        <div class="guidance-title">📊 Cases Identified</div>
        <div class="guidance-content">{guidance.get('cases_identified', 0)} cases</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🏥 Department Actions</div>
        <div class="guidance-content">{guidance.get('department_actions', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">📦 Inventory</div>
        <div class="guidance-content">{guidance.get('inventory_arrangements', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">👨‍⚕️ Resource Deployment</div>
        <div class="guidance-content">{guidance.get('resource_deployment', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🤝 Coordination</div>
        <div class="guidance-content">{guidance.get('coordination_plan', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">💰 Budget</div>
        <div class="guidance-content">{guidance.get('budget_allocation', 'N/A')}</div>
    </div>
    """

def format_guidance_scmo(guidance):
    return f"""
    <div class="guidance-section">
        <div class="guidance-title">🌍 State Overview</div>
        <div class="guidance-content">{guidance.get('state_overview', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🔴 Highly Affected Districts</div>
        <div class="guidance-content">{guidance.get('highly_affected_districts', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">📈 Comparative Analysis</div>
        <div class="guidance-content">{guidance.get('comparative_analysis', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">💊 State Remedies</div>
        <div class="guidance-content">{guidance.get('state_level_remedies', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">👨‍⚕️ Medical Deployment</div>
        <div class="guidance-content">{guidance.get('medical_professional_deployment', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">⚠️ Emergency Measures</div>
        <div class="guidance-content">{guidance.get('emergency_measures', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">🔗 Inter-District Coordination</div>
        <div class="guidance-content">{guidance.get('inter_district_coordination', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">💰 Emergency Funding</div>
        <div class="guidance-content">{guidance.get('emergency_funding', 'N/A')}</div>
    </div>
    <div class="guidance-section">
        <div class="guidance-title">📅 Timeline</div>
        <div class="guidance-content">{guidance.get('timeline_and_milestones', 'N/A')}</div>
    </div>
    """

# Login Page
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="header-main"><h1>🏥 Aayura</h1><p>Disease Outbreak Forecasting & Management System</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login")
        
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_pass")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Login", use_container_width=True):
                if username and password:
                    success, result = login_api(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.session_state.chat_history = []
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Please enter username and password")
        
        with col_b:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        # Demo users info
        st.markdown("---")
        st.markdown("### 📋 Demo Users")
        col_u1, col_u2, col_u3 = st.columns(3)
        
        with col_u1:
            st.markdown("""
            **Seeta Devi**
            - Role: ASHA
            - User: seeta
            - Pass: 123456
            """)
        
        with col_u2:
            st.markdown("""
            **Rahul Gupta**
            - Role: DCMO
            - User: rahul
            - Pass: 123456
            """)
        
        with col_u3:
            st.markdown("""
            **Akshita Mishra**
            - Role: SCMO
            - User: akshita
            - Pass: 123456
            """)

# Signup Page
def show_signup():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="header-main"><h1>🏥 Aayura</h1><p>Create Your Account</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 📝 Sign Up")
        
        col_a, col_b = st.columns(2)
        with col_a:
            first_name = st.text_input("First Name", placeholder="Your first name")
        with col_b:
            last_name = st.text_input("Last Name", placeholder="Your last name")
        
        username = st.text_input("Username", placeholder="Choose a unique username")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        locations = get_locations_api()
        states = sorted(list(set([loc['state'] for loc in locations]))) if locations else []
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            state = st.selectbox("State", states if states else ["No states available"])
            districts = sorted(list(set([loc['district'] for loc in locations if loc['state'] == state]))) if state in [l['state'] for l in locations] else []
            district = st.selectbox("District", districts if districts else ["Select a state first"])
        
        with col_d:
            role = st.selectbox("Role", ["ASHA", "DCMO", "SCMO"])
        
        if st.button("✅ Create Account", use_container_width=True):
            if all([first_name, last_name, username, password, confirm_pass, state, district]):
                if password != confirm_pass:
                    st.error("❌ Passwords don't match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    success, message = signup_api(first_name, last_name, username, password, district, state, role)
                    if success:
                        st.success(message)
                        st.session_state.show_signup = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please fill all fields")
        
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

# Chat Page
def show_chat():
    user = st.session_state.user
    
    # Header with user info
    st.markdown(f'<div class="header-main"><h1>🏥 Aayura - Chat Interface</h1><p>Welcome {user["first_name"]} {user["last_name"]} {get_role_emoji(user["role"])}</p></div>', unsafe_allow_html=True)
    
    # Sidebar with user details
    with st.sidebar:
        st.markdown("### 👤 Your Profile")
        st.markdown(f"""
        <div class="user-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="info-item">
                    <div class="info-label">Name</div>
                    <div class="info-value">{user['first_name']} {user['last_name']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Username</div>
                    <div class="info-value">{user['username']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Role</div>
                    <div class="info-value">{get_role_emoji(user['role'])} {user['role']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Location</div>
                    <div class="info-value">📍 {user['district']}</div>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <div class="info-label">State</div>
                    <div class="info-value">{user['state']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Load default guidance if chat is empty
    if not st.session_state.chat_history:
        st.markdown('<div class="message-system">📨 Loading your initial guidance...</div>', unsafe_allow_html=True)
        
        guidance_data = fetch_guidance_api(
            user['username'],
            '123456',
            user['district'],
            user['state']
        )
        
        if guidance_data:
            st.session_state.chat_history.append({
                'type': 'system',
                'content': f"Welcome {user['first_name']}! 👋 Here's your role-specific guidance for {user['district']}, {user['state']}."
            })
            
            if guidance_data.get('forecast'):
                st.session_state.chat_history.append({
                    'type': 'forecast',
                    'content': guidance_data['forecast']
                })
            
            if guidance_data.get('guidance'):
                st.session_state.chat_history.append({
                    'type': 'guidance',
                    'content': guidance_data['guidance'],
                    'role': user['role']
                })
            
            st.rerun()
    
    # Display chat history
    st.markdown("### 💬 Chat History")
    
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'system':
                st.markdown(f'<div class="message-system">{message["content"]}</div>', unsafe_allow_html=True)
            
            elif message['type'] == 'user':
                st.markdown(f'<div class="message-user">👤 {message["content"]}</div>', unsafe_allow_html=True)
            
            elif message['type'] == 'forecast':
                st.markdown(format_forecast(message['content']), unsafe_allow_html=True)
            
            elif message['type'] == 'guidance':
                role = message['role']
                guidance = message['content']
                
                if role == 'ASHA':
                    st.markdown(format_guidance_asha(guidance), unsafe_allow_html=True)
                elif role == 'DCMO':
                    st.markdown(format_guidance_dcmo(guidance), unsafe_allow_html=True)
                elif role == 'SCMO':
                    st.markdown(format_guidance_scmo(guidance), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Message input
    st.markdown("### 📝 Send Message")
    
    col_msg, col_btn = st.columns([5, 1])
    
    with col_msg:
        user_message = st.text_input(
            "Type your message...",
            placeholder="Ask for remedies, guidance, or type 'reload' for fresh guidance",
            key=f"msg_{len(st.session_state.chat_history)}"
        )
    
    with col_btn:
        send = st.button("📤 Send", use_container_width=True)
    
    if send and user_message:
        # Add user message
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_message
        })
        
        # Check if message contains keywords
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ['guidance', 'reload', 'remedy', 'remedies', 'action', 'what', 'suggest', 'implement', 'help', 'recommend']):
            # Fetch guidance
            st.session_state.chat_history.append({
                'type': 'system',
                'content': '⏳ Fetching role-specific guidance...'
            })
            
            guidance_data = fetch_guidance_api(
                user['username'],
                '123456',
                user['district'],
                user['state']
            )
            
            if guidance_data:
                if guidance_data.get('forecast'):
                    st.session_state.chat_history.append({
                        'type': 'forecast',
                        'content': guidance_data['forecast']
                    })
                
                if guidance_data.get('guidance'):
                    st.session_state.chat_history.append({
                        'type': 'guidance',
                        'content': guidance_data['guidance'],
                        'role': user['role']
                    })
            else:
                st.session_state.chat_history.append({
                    'type': 'system',
                    'content': '❌ Could not fetch guidance. Please try again.'
                })
        else:
            st.session_state.chat_history.append({
                'type': 'system',
                'content': f'💡 Try asking for "guidance", "remedies", "actions", or type "reload" for fresh information!'
            })
        
        st.rerun()

# Main app logic
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        show_signup()
    else:
        show_login()
else:
    show_chat()
