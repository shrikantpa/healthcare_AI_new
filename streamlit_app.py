"""
Streamlit UI for Healthcare AI Malaria Outbreak Forecasting System
Redesigned with Profile Initials, Service Requests, and Simplified Chat
"""
import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="Aayura - Disease Outbreak Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        padding: 0;
    }
    
    /* Header */
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
    }
    
    .header-main h1 {
        font-size: 36px;
        font-weight: 600;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    
    .header-main p {
        font-size: 15px;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Profile Card - Initials Only */
    .profile-initials {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .profile-avatar {
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: 700;
        border: 2px solid white;
    }
    
    .profile-text {
        display: flex;
        flex-direction: column;
    }
    
    .profile-text .role {
        font-size: 12px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .profile-text .initials {
        font-size: 18px;
        font-weight: 700;
    }
    
    /* Chat Container with Boundary */
    .chat-boundary {
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 15px;
        background: #f9f9f9;
        margin: 15px 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Messages */
    .message-ai {
        background: #e8e8e8;
        color: #333;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        margin-right: 60px;
        border-left: 4px solid #667eea;
    }
    
    .message-user {
        background: #c8e6c9;
        color: #1b5e20;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        margin-left: 60px;
        text-align: right;
        border-right: 4px solid #4caf50;
    }
    
    .message-tag {
        font-weight: 700;
        font-size: 12px;
        margin-bottom: 4px;
        opacity: 0.8;
    }
    
    .message-content {
        font-size: 15px;
        line-height: 1.8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Outbreak Card */
    .outbreak-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    
    .outbreak-title {
        font-weight: 700;
        color: #e65100;
        margin-bottom: 10px;
    }
    
    .outbreak-stat {
        display: inline-block;
        background: white;
        padding: 8px 12px;
        border-radius: 6px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    
    .outbreak-stat-label {
        font-weight: 700;
        color: #666;
    }
    
    .outbreak-stat-value {
        color: #ff9800;
        font-weight: 700;
    }
    
    /* Service Request Form */
    .service-form {
        background: #f0f4f8;
        border: 1px solid #667eea;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
    
    .service-form-title {
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
        font-size: 13px;
        text-transform: uppercase;
    }
    
    /* Input Area */
    .input-area {
        background: #f5f7fa;
        padding: 15px;
        border-radius: 12px;
        margin-top: 15px;
        border: 1px solid #e0e0e0;
    }
    
    /* Icon Buttons */
    .icon-btn {
        display: inline-block;
        font-size: 20px;
        cursor: pointer;
        background: none;
        border: none;
        padding: 5px 10px;
    }
    
    .icon-btn:hover {
        opacity: 0.7;
    }
    
    /* Pending Requests */
    .pending-request {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 12px;
    }
    
    .pending-request-header {
        font-weight: 700;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .request-status {
        display: inline-block;
        background: #ffc107;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }
    
    .escalate-btn {
        background: #ff9800;
        color: white;
        border: none;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        cursor: pointer;
        font-weight: 700;
    }
    
    .escalate-btn:hover {
        background: #f57c00;
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
if 'service_requests' not in st.session_state:
    st.session_state.service_requests = []

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

def check_outbreak_api(username, password):
    """Check if outbreak exists - returns ONLY outbreak data"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/outbreak-check",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_actions_api(username, password, question=None):
    """Get role-specific actions for current situation"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/action",
            json={"username": username, "password": password, "question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def submit_service_request_api(username, password, request_item, request_details):
    """Submit a service request"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/service-request?username={username}&password={password}",
            json={"request_item": request_item, "request_details": request_details},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_service_requests_api(username, password):
    """Get user's service requests"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/service-requests?username={username}&password={password}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('requests', [])
        return []
    except:
        return []

def escalate_request_api(username, password, request_id):
    """Escalate a service request"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/service-request/{request_id}/escalate?username={username}&password={password}",
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_user_initials(first_name, last_name):
    """Get user initials from name"""
    return f"{first_name[0].upper()}{last_name[0].upper()}" if first_name and last_name else "??"

# Login Page
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="header-main"><h1>Aayura</h1><p>Disease Outbreak Forecasting & Management System</p></div>', unsafe_allow_html=True)
        
        st.markdown("### Login")
        
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Login", use_container_width=True):
                if username and password:
                    success, result = login_api(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.session_state.chat_history = []
                        st.session_state.service_requests = []
                        st.session_state.outbreak_loaded = False
                        st.success("Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
                else:
                    st.warning("Please enter username and password")
        
        with col_b:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        # Demo users info
        st.markdown("---")
        st.markdown("### Demo Users")
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
        st.markdown('<div class="header-main"><h1>Aayura</h1><p>Create Your Account</p></div>', unsafe_allow_html=True)
        
        st.markdown("### Sign Up")
        
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
        
        if st.button("Create Account", use_container_width=True):
            if all([first_name, last_name, username, password, confirm_pass, state, district]):
                if password != confirm_pass:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = signup_api(first_name, last_name, username, password, district, state, role)
                    if success:
                        st.success(message)
                        st.session_state.show_signup = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {message}")
            else:
                st.warning("Please fill all fields")
        
        if st.button("Back to Login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

# Chat Page - New Implementation
def show_chat():
    user = st.session_state.user
    
    # Sidebar: Profile with initials + logout + service request form
    with st.sidebar:
        # Profile with initials
        initials = get_user_initials(user['first_name'], user['last_name'])
        st.markdown(f"""
        <div class="profile-initials">
            <div class="profile-avatar">{initials}</div>
            <div class="profile-text">
                <div class="role">{user['role']}</div>
                <div class="initials">{initials}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout as small icon
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Logout", help="Logout", use_container_width=False):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.chat_history = []
                st.session_state.service_requests = []
                st.rerun()
        
        st.markdown("---")
        
        # Service Request Form
        st.markdown("### Click here for help")
        with st.form("service_request_form"):
            request_item = st.text_input("Request Item", placeholder="e.g., Medical Supplies, PPE")
            request_details = st.text_area("Details", placeholder="Describe your request", height=80)
            
            if st.form_submit_button("Submit Request", use_container_width=True):
                if request_item and request_details:
                    success, result = submit_service_request_api(
                        user['username'],
                        '123456',
                        request_item,
                        request_details
                    )
                    if success:
                        st.success(f"Request #{result['request_id']} submitted!")
                        st.session_state.service_requests.append(result)
                    else:
                        st.error(f"Failed to submit: {result}")
                else:
                    st.warning("Please fill all fields")
        
        st.markdown("---")
        
        # Pending Requests
        st.markdown("### Pending Requests")
        requests = get_service_requests_api(user['username'], '123456')
        
        if requests:
            for req in requests:
                if req['status'] == 'pending':
                    with st.container():
                        st.markdown(f"""
                        <div class="pending-request">
                            <div class="pending-request-header">
                                <strong>#{req['request_id']}: {req['request_item']}</strong>
                                <br/>
                                <small>Level: {req['escalation_level']}/3</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if req['escalation_level'] < 3:
                            if st.button("Escalate", key=f"escalate_{req['request_id']}", use_container_width=True):
                                success, result = escalate_request_api(
                                    user['username'],
                                    '123456',
                                    req['request_id']
                                )
                                if success:
                                    st.success(f"Request escalated to level {result['new_escalation_level']}")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {result}")
        else:
            st.info("No pending requests")
    
    # Main content area
    st.markdown('<div class="header-main"><h1>Aayura - Chat</h1></div>', unsafe_allow_html=True)
    
    # Load outbreak data on first page load
    if not st.session_state.outbreak_loaded:
        st.session_state.chat_history = []
        
        outbreak_data = check_outbreak_api(
            user['username'],
            '123456',
            user['district'],
            user['state']
        )
        
        if outbreak_data and outbreak_data.get('forecast'):
            forecast = outbreak_data['forecast']
            
            # Display outbreak card with counts
            outbreak_html = f"""
            <div class="outbreak-card">
                <div class="outbreak-title">Outbreak Status: <strong>{forecast['outbreak_status'].upper()}</strong></div>
                <div class="outbreak-stats">
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Total Cases:</span>
                        <span class="outbreak-stat-value">{forecast['total_expected_cases']}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Male:</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_gender'].get('male', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Female:</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_gender'].get('female', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Children (0-5):</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_age_group'].get('children_0_5', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Youth (5-18):</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_age_group'].get('youth_5_18', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Adults (18-60):</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_age_group'].get('adults_18_60', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Elderly (60+):</span>
                        <span class="outbreak-stat-value">{forecast['forecast_by_age_group'].get('elderly_60_plus', 0)}</span>
                    </div>
                    <div class="outbreak-stat">
                        <span class="outbreak-stat-label">Confidence:</span>
                        <span class="outbreak-stat-value">{forecast['confidence_level']}%</span>
                    </div>
                </div>
            </div>
            """
            
            st.markdown(outbreak_html, unsafe_allow_html=True)
            st.session_state.chat_history.append({
                'type': 'outbreak',
                'content': outbreak_data
            })
        else:
            st.warning("⚠️ Could not load outbreak data")
        
        st.session_state.outbreak_loaded = True
    
    # Chat boundary
    st.markdown('<div class="chat-boundary">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['type'] == 'outbreak':
            # Already displayed above
            pass
        elif message['type'] == 'user':
            st.markdown(f"""
            <div class="message-user">
                <div class="message-tag">user:</div>
                <div class="message-content">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        elif message['type'] == 'ai':
            # Format AI actions based on role
            actions = message['content']
            actions_html = "<br/>".join([f"• {action}" for action in actions]) if isinstance(actions, list) else str(actions)
            
            st.markdown(f"""
            <div class="message-ai">
                <div class="message-tag">Aayura:</div>
                <div class="message-content">{actions_html}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Message input at bottom - Aligned horizontally
    col_msg, col_btn = st.columns([5, 1], gap="small")
    
    with col_msg:
        user_input = st.text_input(
            "Ask a Question",
            placeholder="e.g., What remedies should I recommend?",
            key=f"user_msg_{len(st.session_state.chat_history)}",
            label_visibility="collapsed"
        )
    
    with col_btn:
        send_btn = st.button("Send", use_container_width=True, key="send_btn")
    
    if send_btn and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_input
        })
        
        # Call /action endpoint to get role-specific actions
        action_data = get_actions_api(
            user['username'],
            '123456',
            user['district'],
            user['state'],
            user_input
        )
        
        if action_data and action_data.get('actions'):
            # Format actions for display based on role
            actions = action_data['actions']
            
            if user['role'] == 'ASHA':
                action_list = [
                    f"General Remedies: {actions.get('general_remedies', 'N/A')}",
                    f"Social Measures: {actions.get('social_remedies', 'N/A')}",
                    f"Govt Actions: {actions.get('govt_regulatory_actions', 'N/A')}",
                    f"Healthcare: {actions.get('healthcare_body_actions', 'N/A')}"
                ]
            elif user['role'] == 'DCMO':
                action_list = [
                    f"Cases: {actions.get('cases_identified', 'N/A')}",
                    f"Dept Actions: {actions.get('department_actions', 'N/A')}",
                    f"Inventory: {actions.get('inventory_arrangements', 'N/A')}",
                    f"Resources: {actions.get('resource_deployment', 'N/A')}",
                    f"Coordination: {actions.get('coordination_plan', 'N/A')}",
                    f"Budget: {actions.get('budget_allocation', 'N/A')}"
                ]
            elif user['role'] == 'SCMO':
                action_list = [
                    f"Overview: {actions.get('state_overview', 'N/A')}",
                    f"Affected: {actions.get('highly_affected_districts', 'N/A')}",
                    f"Analysis: {actions.get('comparative_analysis', 'N/A')}",
                    f"Remedies: {actions.get('state_level_remedies', 'N/A')}",
                    f"Medical: {actions.get('medical_professional_deployment', 'N/A')}",
                    f"Emergency: {actions.get('emergency_measures', 'N/A')}",
                    f"Inter-District: {actions.get('inter_district_coordination', 'N/A')}",
                    f"Funding: {actions.get('emergency_funding', 'N/A')}",
                    f"Timeline: {actions.get('timeline_and_milestones', 'N/A')}"
                ]
            else:
                action_list = [str(actions)]
            
            st.session_state.chat_history.append({
                'type': 'ai',
                'content': action_list
            })
        else:
            st.error("Failed to get actions. Please try again.")
        
        st.rerun()

# Main app logic
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        show_signup()
    else:
        show_login()
else:
    show_chat()
