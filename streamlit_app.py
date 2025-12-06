
"""
Single-file app: Streamlit UI + SQLite data layer for Aayura - Disease Outbreak Management
Implements:
  - Login/Signup (with location validation)
  - Outbreak bootstrap (single AI message at bottom, non-blocking)
  - Smooth chat (disables input while processing; no screen freeze)
  - Sidebar: profile + inline Logout + service requests

Run:
    streamlit run app.py
"""

import streamlit as st
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import time

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aayura - Disease Outbreak Management",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Database Layer (merged from your database.py and upgraded)
# -----------------------------------------------------------------------------
class DatabaseManager:
    def __init__(self, db_path: str = "MALERIA.db"):
        self.db_path = db_path
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Location table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                UNIQUE(state, district)
            )
        ''')
        # Malaria Data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS malaria_state_data (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                cases_examined INTEGER NOT NULL,
                cases_detected INTEGER NOT NULL,
                male_case_examined INTEGER NOT NULL,
                female_case_examined INTEGER NOT NULL,
                male_case_detected INTEGER NOT NULL,
                female_case_detected INTEGER NOT NULL,
                FOREIGN KEY (location_id) REFERENCES location(location_id),
                UNIQUE(location_id, year)
            )
        ''')
        # Users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                district TEXT NOT NULL,
                state TEXT NOT NULL,
                location_id INTEGER NOT NULL,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES location(location_id),
                UNIQUE(username)
            )
        ''')
        # Service Requests
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                district TEXT NOT NULL,
                state TEXT NOT NULL,
                request_item TEXT NOT NULL,
                request_details TEXT,
                status TEXT DEFAULT 'pending',
                escalation_level INTEGER DEFAULT 0,
                escalated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        self.conn.commit()

    def verify_location(self, district: str, state: str) -> Optional[int]:
        self.cursor.execute(
            '''SELECT location_id FROM location WHERE district = ? AND state = ?''',
            (district, state)
        )
        row = self.cursor.fetchone()
        return int(row['location_id']) if row else None

    def create_user(self, first_name: str, last_name: str, username: str,
                    password: str, district: str, state: str, role: str = 'analyst') -> Optional[Dict]:
        location_id = self.verify_location(district, state)
        if not location_id:
            return None
        try:
            self.cursor.execute('''
                INSERT INTO users
                (first_name, last_name, username, password, district, state, location_id, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, username, password, district, state, location_id, role))
            self.conn.commit()

            self.cursor.execute('''
                SELECT user_id, first_name, last_name, username, district, state, role, created_at
                FROM users WHERE username = ?
            ''', (username,))
            u = self.cursor.fetchone()
            return {
                'user_id': u['user_id'],
                'first_name': u['first_name'],
                'last_name': u['last_name'],
                'username': u['username'],
                'district': u['district'],
                'state': u['state'],
                'role': u['role'],
                'created_at': u['created_at'],
            }
        except sqlite3.IntegrityError:
            return None

    def get_user_by_credentials(self, username: str, password: str) -> Optional[Dict]:
        self.cursor.execute(
            '''SELECT user_id, first_name, last_name, username, district, state, role, created_at
               FROM users WHERE username = ? AND password = ?''',
            (username, password)
        )
        u = self.cursor.fetchone()
        if not u:
            return None
        return {
            'user_id': u['user_id'],
            'first_name': u['first_name'],
            'last_name': u['last_name'],
            'username': u['username'],
            'district': u['district'],
            'state': u['state'],
            'role': u['role'],
            'created_at': u['created_at'],
        }

    def get_district_data(self, district: str, state: Optional[str] = None) -> Dict:
        if state:
            self.cursor.execute('''
                SELECT l.state, l.district, m.year, m.cases_examined,
                       m.cases_detected, m.male_case_examined,
                       m.female_case_examined, m.male_case_detected,
                       m.female_case_detected
                FROM malaria_state_data m
                JOIN location l ON m.location_id = l.location_id
                WHERE l.district = ? AND l.state = ?
                ORDER BY m.year DESC
            ''', (district, state))
        else:
            self.cursor.execute('''
                SELECT l.state, l.district, m.year, m.cases_examined,
                       m.cases_detected, m.male_case_examined,
                       m.female_case_examined, m.male_case_detected,
                       m.female_case_detected
                FROM malaria_state_data m
                JOIN location l ON m.location_id = l.location_id
                WHERE l.district = ?
                ORDER BY m.year DESC
            ''', (district,))
        rows = self.cursor.fetchall()
        if not rows:
            return {}
        result = {
            'district': district,
            'state': rows[0]['state'] if rows else None,
            'years': []
        }
        for r in rows:
            result['years'].append({
                'year': r['year'],
                'cases_examined': r['cases_examined'],
                'cases_detected': r['cases_detected'],
                'male_case_examined': r['male_case_examined'],
                'female_case_examined': r['female_case_examined'],
                'male_case_detected': r['male_case_detected'],
                'female_case_detected': r['female_case_detected'],
            })
        return result

    def get_all_districts(self) -> List[Dict]:
        self.cursor.execute('''
            SELECT DISTINCT state, district FROM location ORDER BY state, district
        ''')
        rows = self.cursor.fetchall()
        return [{'state': r['state'], 'district': r['district']} for r in rows]

    def add_default_users_and_data(self):
        # Seed locations
        seeds = [
            ('Uttar Pradesh', 'Etah'),
            ('Maharashtra', 'Mumbai'),
            ('Maharashtra', 'Pune'),
            ('Delhi', 'New Delhi'),
        ]
        for state, district in seeds:
            # If location exists, skip both location and malaria_state_data
            self.cursor.execute(
                '''SELECT location_id FROM location WHERE state = ? AND district = ?''',
                (state, district)
            )
            loc = self.cursor.fetchone()
            if loc:
                continue  # skip inserts for existing location

            self.cursor.execute('''
                INSERT INTO location (state, district) VALUES (?, ?)
            ''', (state, district))
            self.conn.commit()

            # Insert minimal malaria data for the new location
            self.cursor.execute(
                '''SELECT location_id FROM location WHERE state = ? AND district = ?''',
                (state, district)
            )
            loc = self.cursor.fetchone()
            location_id = int(loc['location_id']) if loc else None
            if location_id:
                for year, ce, cd, mce, fce, mcd, fcd in [
                    (2022, 800, 120, 400, 400, 70, 50),
                    (2023, 1000, 160, 500, 500, 90, 70),
                    (2024, 1200, 200, 600, 600, 110, 90),
                ]:
                    try:
                        self.cursor.execute('''
                            INSERT INTO malaria_state_data
                            (location_id, year, cases_examined, cases_detected,
                             male_case_examined, female_case_examined,
                             male_case_detected, female_case_detected)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (location_id, year, ce, cd, mce, fce, mcd, fcd))
                    except sqlite3.IntegrityError:
                        pass
                self.conn.commit()

        # Add default users if they don't exist
        defaults = [
            ('Bhuwan', 'Thada', 'bhuwan', 'bt12345', 'Etah', 'Uttar Pradesh', 'ASHA'),
            ('Shyam', 'Mishra', 'shyam', 'shyam12345', 'Etah', 'Uttar Pradesh', 'DCMO'),
            ('Amit', 'Gupta', 'amit', 'amit12345', 'Etah', 'Uttar Pradesh', 'SCMO'),
        ]
        for fn, ln, un, pw, dist, state, role in defaults:
            self.cursor.execute('SELECT username FROM users WHERE username = ?', (un,))
            if self.cursor.fetchone():
                continue
            loc_id = self.verify_location(dist, state)
            if not loc_id:
                continue
            self.cursor.execute('''
                INSERT INTO users (first_name, last_name, username, password,
                                   district, state, location_id, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fn, ln, un, pw, dist, state, loc_id, role))
            self.conn.commit()

    def submit_service_request(self, user_id: int, username: str, role: str,
                               district: str, state: str, item: str, details: str) -> int:
        self.cursor.execute('''
            INSERT INTO service_requests
            (user_id, username, role, district, state, request_item, request_details, status, escalation_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0)
        ''', (user_id, username, role, district, state, item, details))
        self.conn.commit()
        return int(self.cursor.lastrowid)

    def get_user_service_requests(self, user_id: int) -> List[Dict]:
        self.cursor.execute('''
            SELECT request_id, request_item, request_details, status, escalation_level, created_at
            FROM service_requests
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = self.cursor.fetchall()
        return [{
            'request_id': r['request_id'],
            'request_item': r['request_item'],
            'request_details': r['request_details'],
            'status': r['status'],
            'escalation_level': r['escalation_level'],
            'created_at': r['created_at'],
            'can_escalate': r['status'] == 'pending'
        } for r in rows]

    def escalate_request(self, request_id: int, user_id: int) -> Tuple[bool, int]:
        self.cursor.execute('''
            SELECT escalation_level, status FROM service_requests
            WHERE request_id = ? AND user_id = ?
        ''', (request_id, user_id))
        row = self.cursor.fetchone()
        if not row:
            return False, -1
        if row['status'] != 'pending':
            return False, -1
        new_level = int(row['escalation_level']) + 1
        if new_level > 3:
            return False, int(row['escalation_level'])
        self.cursor.execute('''
            UPDATE service_requests
            SET escalation_level = ?, escalated_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
        ''', (new_level, request_id))
        self.conn.commit()
        return True, new_level

    def close(self):
        self.conn.close()

# Instantiate DB and seed data
db = DatabaseManager()
db.add_default_users_and_data()

# -----------------------------------------------------------------------------
# Utility & Domain Logic (forecast/actions)
# -----------------------------------------------------------------------------
def compute_outbreak_forecast(district_data: Dict) -> Optional[Dict]:
    """Deterministic summary from available data; replaces LLM calls."""
    if not district_data or not district_data.get('years'):
        return None
    latest = district_data['years'][0]
    total_expected_cases = int(latest.get('cases_detected', 0)) + int(latest.get('cases_examined', 0) // 10)
    forecast_by_gender = {
        'male': int(latest.get('male_case_detected', 0)),
        'female': int(latest.get('female_case_detected', 0)),
    }
    # simple split by age groups proportional to detected
    det = int(latest.get('cases_detected', 0))
    age_split = {
        'children_0_5': int(det * 0.12),
        'youth_5_18': int(det * 0.24),
        'adults_18_60': int(det * 0.54),
        'elderly_60_plus': int(det * 0.10),
    }
    return {
        'status': 'potential_outbreak' if det > 100 else 'no_outbreak_observed',
        'district': district_data.get('district'),
        'state': district_data.get('state'),
        'forecast': {
            'outbreak_status': 'High' if det > 150 else ('Moderate' if det > 80 else 'Low'),
            'disease': 'Malaria',
            'total_expected_cases': total_expected_cases,
            'forecast_by_gender': forecast_by_gender,
            'forecast_by_age_group': age_split,
        }
    }

def generate_role_actions(role: str, forecast: Dict, district: str, state: str, question: Optional[str] = None) -> List[str]:
    """Format actions per role for chat display."""
    if not forecast:
        return ["No forecast data available."]
    f = forecast
    lines = []
    if role == 'ASHA':
        lines = [
            f"General Remedies: Use mosquito nets, apply repellent, maintain hygiene.",
            f"Social Measures: Organize community cleanups and awareness camps.",
            f"Govt Actions: Conduct free medical camps and source inspections.",
            f"Healthcare: Stock antimalarials, testing kits, ensure beds & staff."
        ]
    elif role == 'DCMO':
        lines = [
            f"Cases: {f.get('total_expected_cases', 'N/A')}",
            f"Dept Actions: Activate district surveillance & testing centers.",
            f"Inventory: Prepare doses/kits aligned to expected cases.",
            f"Resources: Deploy doctors, nurses, paramedics across the district.",
            f"Coordination: Work with local administration for compliance.",
            f"Budget: Allocate emergency procurement funds."
        ]
    elif role == 'SCMO':
        lines = [
            "Overview: State-wide monitoring & rapid response.",
            "Affected: Identify top high-risk districts from latest data.",
            "Analysis: Compare infection rates district-wise.",
            "Remedies: Launch state-level awareness & preventive drives.",
            "Medical: Surge medical staff to hotspots.",
            "Emergency: Stand up rapid testing & quarantine facilities.",
            "Inter-District: Enable resource sharing between districts.",
            "Funding: Sanction emergency funds.",
            "Timeline: Week 1 assessment, Week 2-4 deployment."
        ]
    else:
        lines = [json.dumps(f, indent=2)]
    return lines

# -----------------------------------------------------------------------------
# Session State
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'password' not in st.session_state:
    st.session_state.password = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'outbreak_loaded' not in st.session_state:
    st.session_state.outbreak_loaded = False
if 'current_input' not in st.session_state:
    st.session_state.current_input = ""
if 'service_requests' not in st.session_state:
    st.session_state.service_requests = []
if 'bootstrapping' not in st.session_state:
    st.session_state.bootstrapping = False
if 'msg_processing' not in st.session_state:
    st.session_state.msg_processing = False
if 'prefetched_requests' not in st.session_state:
    st.session_state.prefetched_requests = []

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_user_initials(first_name: str, last_name: str) -> str:
    return f"{(first_name or '?')[0].upper()}{(last_name or '?')[0].upper()}"

def bootstrap_user_session(user_obj: dict, password: str):
    """
    Prepare data BEFORE flipping logged_in to True:
    - outreak forecast message
    - prefetch service requests
    - reset chat history with single AI message at bottom
    """
    st.session_state.bootstrapping = True
    try:
        with st.spinner("Preparing your workspace..."):
            district_data = db.get_district_data(user_obj.get('district', ''), user_obj.get('state', ''))
            outbreak = compute_outbreak_forecast(district_data)

            st.session_state.chat_history = []
            if outbreak and outbreak.get('forecast'):
                f = outbreak['forecast']
                ai_lines = [
                    f"Outbreak Status: {f.get('outbreak_status', '').upper()}",
                    f"Disease: {f.get('disease', 'Malaria')}",
                    f"Total Cases: {f.get('total_expected_cases', 0)}",
                    f"Male: {f.get('forecast_by_gender', {}).get('male', 0)}",
                    f"Female: {f.get('forecast_by_gender', {}).get('female', 0)}",
                    f"Children (0-5): {f.get('forecast_by_age_group', {}).get('children_0_5', 0)}",
                    f"Youth (5-18): {f.get('forecast_by_age_group', {}).get('youth_5_18', 0)}",
                    f"Adults (18-60): {f.get('forecast_by_age_group', {}).get('adults_18_60', 0)}",
                    f"Elderly (60+): {f.get('forecast_by_age_group', {}).get('elderly_60_plus', 0)}",
                ]
                st.session_state.chat_history.append({'type': 'ai', 'content': ai_lines})
            else:
                st.session_state.chat_history.append({'type': 'ai', 'content': ["No outbreak data available at the moment."]})

            # Prefetch service requests
            st.session_state.prefetched_requests = db.get_user_service_requests(user_obj['user_id'])
            st.session_state.outbreak_loaded = True
    finally:
        st.session_state.bootstrapping = False

# -----------------------------------------------------------------------------
# Auth UI
# -----------------------------------------------------------------------------

def show_login():
    # --- SAFE INITIALIZATION BEFORE WIDGETS ---
    if 'login_user' not in st.session_state:
        st.session_state['login_user'] = ""
    if 'login_pass' not in st.session_state:
        st.session_state['login_pass'] = ""

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Aayura\n\nDisease Outbreak Forecasting & Management System")
        st.markdown("### Login")

        # Use existing session_state values as defaults (no post-instantiation writes)
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_user"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_pass"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", use_container_width=True):
                if username and password:
                    user = db.get_user_by_credentials(username, password)
                    if user:
                        # Prepare session FIRST to avoid flicker
                        st.session_state.user = user
                        st.session_state.password = password
                        st.session_state.show_signup = False

                        # Bootstrap all data BEFORE flipping logged_in
                        bootstrap_user_session(user, password)

                        # Flip login flag; DO NOT write to login_user/login_pass here
                        st.session_state.logged_in = True

                        # IMPORTANT: do NOT clear st.session_state['login_user'] or ['login_pass']
                        # Just rerun to render the chat screen (login widgets won't be shown)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Please enter username and password")

        with col_b:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()

def show_signup():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Aayura\n\nCreate Your Account")
        st.markdown("### Sign Up")

        col_a, col_b = st.columns(2)
        with col_a:
            first_name = st.text_input("First Name", placeholder="Your first name")
        with col_b:
            last_name = st.text_input("Last Name", placeholder="Your last name")

        username = st.text_input("Username", placeholder="Choose a unique username")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

        # Locations (from DB)
        locations = db.get_all_districts()
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
                    # Validate role
                    if role not in ['ASHA', 'DCMO', 'SCMO']:
                        st.error("Invalid role. Must be one of: ASHA, DCMO, SCMO")
                    else:
                        loc_id = db.verify_location(district, state)
                        if not loc_id:
                            st.error(f"Location not found: District '{district}' in State '{state}'")
                        else:
                            new_user = db.create_user(first_name, last_name, username, password, district, state, role)
                            if new_user:
                                st.success(f"User {username} created successfully!")
                                st.session_state.show_signup = False
                                time.sleep(0.8)
                                st.rerun()
                            else:
                                st.error(f"Username '{username}' already exists or database error occurred")
            else:
                st.warning("Please fill all fields")

    if st.button("Back to Login", use_container_width=True):
        st.session_state.show_signup = False
        st.rerun()

# -----------------------------------------------------------------------------
# Chat UI
# -----------------------------------------------------------------------------
def process_chat_message():
    """
    Process current input; disable input while calling actions; add AI message; clear input.
    """
    if st.session_state.msg_processing:
        return

    user_input = (st.session_state.current_input or "").strip()
    if not user_input:
        return

    st.session_state.msg_processing = True
    try:
        user = st.session_state.user
        # add user message
        st.session_state.chat_history.append({'type': 'user', 'content': user_input})

        # derive actions from forecast for role
        with st.spinner("Getting actions..."):
            district_data = db.get_district_data(user.get('district', ''), user.get('state', ''))
            outbreak = compute_outbreak_forecast(district_data)
            forecast = outbreak.get('forecast') if outbreak else None
            action_list = generate_role_actions(user.get('role', ''), forecast or {}, user.get('district', ''), user.get('state', ''), user_input)

        # add ai message
        st.session_state.chat_history.append({'type': 'ai', 'content': action_list})
    finally:
        st.session_state.current_input = ""
        st.session_state.msg_processing = False

def show_chat():
    user = st.session_state.user

    # Sidebar with inline profile + logout
    with st.sidebar:
        initials = get_user_initials(user['first_name'], user['last_name'])
        prof_col, logout_col = st.columns([5, 2])
        with prof_col:
            st.markdown(f"**{initials}** · {user.get('role','').upper()}")
        with logout_col:
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.password = None
                st.session_state.chat_history = []
                st.session_state.service_requests = []
                st.session_state.prefetched_requests = []
                st.session_state.outbreak_loaded = False
                st.session_state.current_input = ""
                st.session_state.msg_processing = False
                st.rerun()

        st.markdown("---")

        # Service Request Form
        st.markdown("### Click here for help")
        with st.form("service_request_form"):
            request_item = st.text_input("Request Item", placeholder="e.g., Medical Supplies, PPE")
            request_details = st.text_area("Details", placeholder="Describe your request", height=80)
            if st.form_submit_button("Submit Request", use_container_width=True):
                if request_item and request_details:
                    req_id = db.submit_service_request(
                        user_id=user['user_id'],
                        username=user['username'],
                        role=user['role'],
                        district=user['district'],
                        state=user['state'],
                        item=request_item,
                        details=request_details
                    )
                    st.success(f"Request #{req_id} submitted!")
                    # refresh pending requests list
                    st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])
                    st.rerun()
                else:
                    st.warning("Please fill all fields")

        st.markdown("---")

        # Pending Requests
        st.markdown("### Pending Requests")
        requests = st.session_state.prefetched_requests
        if requests:
            any_pending = False
            for req in requests:
                if req.get('status') == 'pending':
                    any_pending = True
                    with st.container(border=True):
                        st.markdown(f"**#{req['request_id']}**: {req['request_item']}")
                        st.markdown(f"Level: {req['escalation_level']}/3")
                        if req['escalation_level'] < 3:
                            if st.button("Escalate", key=f"escalate_btn_{req['request_id']}", use_container_width=True):
                                ok, new_level = db.escalate_request(req['request_id'], user['user_id'])
                                if ok:
                                    st.success(f"Request escalated to level {new_level}")
                                    st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])
                                    st.rerun()
                                else:
                                    st.error("Unable to escalate request.")
            if not any_pending:
                st.info("No pending requests")
        else:
            st.info("No pending requests")

    # Main content area
    st.markdown("## Aayura - Chat")

    # Display chat history (single AI outbreak message was added during bootstrap)
    st.markdown("")
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            st.markdown(f"**You:**\n\n{message['content']}")
        elif message['type'] == 'ai':
            actions = message['content']
            actions_html = "\n".join([f"• {a}" for a in actions]) if isinstance(actions, list) else str(actions)
            st.markdown(f"**Aayura:**\n\n{actions_html}")
        st.markdown("")

    st.markdown("---")

    # Input row - disabled while processing
    col_msg, col_btn = st.columns([5, 1], gap="small")
    with col_msg:
        st.text_input(
            "Ask a Question",
            placeholder="e.g., What remedies should I recommend?",
            key="current_input",
            label_visibility="collapsed",
            disabled=st.session_state.msg_processing,
        )
    with col_btn:
        st.button(
            "Send",
            use_container_width=True,
            on_click=process_chat_message,
            key="send_btn_callback",
            disabled=st.session_state.msg_processing,
        )

# -----------------------------------------------------------------------------
# App Router
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        show_signup()
    else:
        show_login()
else:
    show_chat()
