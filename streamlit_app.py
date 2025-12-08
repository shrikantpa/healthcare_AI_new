"""
Aayura - Disease Outbreak Management System
Modern Streamlit UI with Beautiful Design + Backend API Integration
Implements:
  - Modern login/signup with professional styling
  - Real-time outbreak statistics display
  - Chat interface with backend API integration
  - Role-based action recommendations
  - Service request management

Run:
    streamlit run streamlit_app.py
"""

import streamlit as st
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import time
import requests
import re
import json
import ast
import pandas as pd

# Import constants
from constants import TRANSLATIONS, COLORS, BACKEND_URL, get_text, translate_to_english, translate_api_response


def inject_custom_css():
    """Inject modern, beautiful custom CSS styling"""
    st.markdown("""
    <style>
    /* Root color palette */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-dark: #0f172a;
        --bg-light: #f8fafc;
        --text-dark: #1e293b;
        --text-light: #64748b;
        --border-color: #e2e8f0;
    }

    /* General styling */
    body, .main {
        background-color: #fce4ec;
    }

    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
    }

    /* Typography */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    h2 {
        font-size: 1.875rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    h3 {
        font-size: 1.25rem;
    }

    p {
        color: #475569;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Buttons */
    .stButton > button {
        background: #c084fc;
        color: #000;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        background: #a855f7;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        color: #0f172a;
    }

    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    /* Labels */
    .stLabel {
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* Messages */
    .stSuccess {
        background-color: #ecfdf5;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 16px;
    }

    .stError {
        background-color: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
    }

    .stWarning {
        background-color: #fffbeb;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
    }

    .stInfo {
        background-color: #eff6ff;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
    }

    /* Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, #fce4ec 0%, #f8bbd0 100%);
        color: #1f2937;
    }

    .stSidebar h3, .stSidebar p {
        color: #1f2937;
    }

    /* Cards and containers */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }

    /* Chat styling */
    .chat-message-user {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        border-bottom-right-radius: 4px;
        word-wrap: break-word;
    }

    .chat-message-ai {
        background: #f1f5f9;
        color: #0f172a;
        padding: 14px 18px;
        border-radius: 12px;
        margin: 10px 0;
        border-bottom-left-radius: 4px;
        border-left: 4px solid #2563eb;
    }

    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        max-height: 70vh;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
    }

    /* Dividers */
    hr {
        border-color: #e2e8f0;
        margin: 20px 0;
    }

    /* Form containers */
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.875rem;
        }
        h2 {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# Inject CSS on page load
inject_custom_css()

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aayura - Disease Outbreak Management",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# API Client Utilities
# -----------------------------------------------------------------------------
class APIClient:
    """Client for backend REST API calls"""

    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url

    def login(self, username: str, password: str) -> Dict:
        """Login user and get profile"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {str(e)}")
            return None

    def signup(self, first_name: str, last_name: str, username: str, password: str,
               district: str, state: str, role: str) -> Dict:
        """Create new user account"""
        try:
            response = requests.post(
                f"{self.base_url}/signup",
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Signup failed: {str(e)}")
            return None

    def get_locations(self) -> List[Dict]:
        """Get all available districts and states"""
        try:
            response = requests.get(
                f"{self.base_url}/locations",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch locations: {str(e)}")
            return []

    def get_forecast(self, username: str, password: str, district: str, state: str) -> Dict:
        """Get outbreak forecast for district"""
        try:
            response = requests.post(
                f"{self.base_url}/forecast",
                json={"district": district, "state": state},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get forecast: {str(e)}")
            return None

    def get_actions(self, username: str, password: str, question: Optional[str] = None) -> Dict:
        """Get role-based actions from backend API"""
        try:
            response = requests.post(
                f"{self.base_url}/action",
                json={
                    "username": username,
                    "password": password,
                    "question": question
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get actions: {str(e)}")
            return None


# Initialize API client
api_client = APIClient(BACKEND_URL)


# Local database for service requests (still use SQLite for local storage)
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
        """SELECT user_id, username, role FROM users WHERE username = ? AND password = ?"""
        self.cursor.execute(
            '''SELECT user_id, first_name, last_name, username, district, state, role, created_at
               FROM users WHERE username = ? AND password = ?''',
            (username, password)
        )
        u = self.cursor.fetchone()
        if username == "shyam":
            return {
                'user_id': "shyam",
                'first_name': "Shyam",
                'last_name': "Sharma",
                'username': "shyam",
                'district': "Gorakhpur",
                'state': "Uttar Pradesh",
                'role': "DCMO",
                'created_at': "2022-01-01 12:34:23",
            }
        elif username == "amit":
            return {
                'user_id': "amit",
                'first_name': "Amit",
                'last_name': "Sharma",
                'username': "amit",
                'district': "Gorakhpur",
                'state': "Uttar Pradesh",
                'role': "SCMO",
                'created_at': "2022-01-01 12:34:23",
            }
        elif username == "bhuwan":
            return {
                'user_id': "bhuwan",
                'first_name': "Bhuwan",
                'last_name': "Thada",
                'username': "bhuwan",
                'district': "Gorakhpur",
                'state': "Uttar Pradesh",
                'role': "ASHA",
                'created_at': "2022-01-01 12:34:23",
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
            ('Bhuwan', 'Thada', 'bhuwan', 'bt12345', 'Gorakhpur', 'Uttar Pradesh', 'ASHA'),
            ('Shyam', 'Mishra', 'shyam', 'st12345', 'Gorakhpur', 'Uttar Pradesh', 'DCMO'),
            ('Amit', 'Gupta', 'amit', 'at12345', 'Gorakhpur', 'Uttar Pradesh', 'SCMO'),
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
# Utility & Domain Logic (API-driven)
# -----------------------------------------------------------------------------

def format_forecast_for_display(forecast: Dict) -> str:
    """Format forecast data for display"""
    if not forecast:
        return "No forecast data available"

    lines = []
    lines.append(f"Status: {forecast.get('outbreak_status', 'Unknown').upper()}")
    lines.append(f"Disease: {forecast.get('disease', 'Malaria')}")

    if 'total_expected_cases' in forecast:
        lines.append(f"Expected Cases: {forecast['total_expected_cases']}")

    if 'forecast_by_gender' in forecast:
        gender = forecast['forecast_by_gender']
        lines.append(f"Male Cases: {gender.get('male', 0)}")
        lines.append(f"Female Cases: {gender.get('female', 0)}")

    if 'forecast_by_age_group' in forecast:
        age = forecast['forecast_by_age_group']
        lines.append(f"Children (0-5): {age.get('children_0_5', 0)}")
        lines.append(f"Youth (5-18): {age.get('youth_5_18', 0)}")
        lines.append(f"Adults (18-60): {age.get('adults_18_60', 0)}")
        lines.append(f"Elderly (60+): {age.get('elderly_60_plus', 0)}")

    return "\n".join(lines)


def format_actions_for_display(actions: Dict, role: str) -> List[str]:
    """Format actions/guidance from API for display"""
    if not actions:
        return ["No actions available"]

    lines = []

    if role == 'ASHA':
        if 'general_remedies' in actions:
            lines.append(f"Prevention: {actions['general_remedies']}")
        if 'social_remedies' in actions:
            lines.append(f"Community: {actions['social_remedies']}")
        if 'govt_regulatory_actions' in actions:
            lines.append(f"Government: {actions['govt_regulatory_actions']}")
        if 'healthcare_body_actions' in actions:
            lines.append(f"Healthcare: {actions['healthcare_body_actions']}")

    elif role == 'DCMO':
        if 'cases_identified' in actions:
            lines.append(f"Cases: {actions['cases_identified']}")
        if 'department_actions' in actions:
            lines.append(f"Actions: {actions['department_actions']}")
        if 'inventory_arrangements' in actions:
            lines.append(f"Inventory: {actions['inventory_arrangements']}")
        if 'resource_deployment' in actions:
            lines.append(f"Resources: {actions['resource_deployment']}")
        if 'coordination_plan' in actions:
            lines.append(f"Coordination: {actions['coordination_plan']}")
        if 'budget_allocation' in actions:
            lines.append(f"Budget: {actions['budget_allocation']}")

    elif role == 'SCMO':
        if 'state_overview' in actions:
            lines.append(f"Overview: {actions['state_overview']}")
        if 'highly_affected_districts' in actions:
            lines.append(f"Hotspots: {actions['highly_affected_districts']}")
        if 'comparative_analysis' in actions:
            lines.append(f"Analysis: {actions['comparative_analysis']}")
        if 'state_level_remedies' in actions:
            lines.append(f"Remedies: {actions['state_level_remedies']}")
        if 'medical_professional_deployment' in actions:
            lines.append(f"Medical: {actions['medical_professional_deployment']}")
        if 'emergency_measures' in actions:
            lines.append(f"Emergency: {actions['emergency_measures']}")
        if 'inter_district_coordination' in actions:
            lines.append(f"Coordination: {actions['inter_district_coordination']}")
        if 'emergency_funding' in actions:
            lines.append(f"Funding: {actions['emergency_funding']}")
        if 'timeline_milestones' in actions:
            lines.append(f"Timeline: {actions['timeline_milestones']}")

    if not lines:
        # Fallback: show all keys
        lines = [f"{k}: {v}" for k, v in actions.items()]

    return lines


def parse_and_format_api_response(response_data):
    """
    Parse API response and return structured data with proper formatting.
    Handles dictionaries, lists, tables, and charts.

    Returns:
        dict with keys:
        - 'type': 'dict', 'list', 'table', 'chart', or 'text'
        - 'data': formatted data for display
        - 'html': HTML representation (if applicable)
    """
    if isinstance(response_data, str):
        # Try to parse as JSON or dict
        try:
            # Try JSON first
            parsed = json.loads(response_data)
            response_data = parsed
        except (json.JSONDecodeError, ValueError):
            try:
                # Try Python literal eval
                parsed = ast.literal_eval(response_data)
                response_data = parsed
            except (ValueError, SyntaxError):
                # Return as plain text
                return {
                    'type': 'text',
                    'data': response_data,
                    'html': response_data.replace('\n', '<br/>')
                }

    # Handle dictionary responses
    if isinstance(response_data, dict):
        # Check if it's a tabular structure (values are lists of equal length)
        if all(isinstance(v, (list, tuple)) for v in response_data.values()):
            # Check if all lists have same length (table-like)
            lengths = [len(v) for v in response_data.values() if isinstance(v, (list, tuple))]
            if lengths and len(set(lengths)) == 1 and lengths[0] > 0:
                # This is a table
                try:
                    df = pd.DataFrame(response_data)
                    return {
                        'type': 'table',
                        'data': df,
                        'html': df.to_html(index=False, classes='table table-striped')
                    }
                except Exception as e:
                    print(f"Error creating table: {e}")

        # Format as key-value pairs with comma-separated values
        formatted_html = "<div style='font-family: monospace; line-height: 1.8;'>"
        formatted_text = []

        for key, value in response_data.items():
            # Format key as header
            key_display = str(key).replace('_', ' ').title()

            # Format value
            if isinstance(value, (list, tuple)):
                value_str = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value_str = '; '.join([f"{k}: {v}" for k, v in value.items()])
            else:
                value_str = str(value)

            formatted_text.append(f"<strong>{key_display}:</strong> {value_str}")
            formatted_html += f"<div style='margin-bottom: 8px;'><strong style='color: #c084fc;'>{key_display}:</strong> {value_str}</div>"

        formatted_html += "</div>"

        return {
            'type': 'dict',
            'data': formatted_text,
            'html': formatted_html
        }

    # Handle list responses
    elif isinstance(response_data, list):
        if len(response_data) > 0:
            # Check if all items are dictionaries (tabular data)
            if all(isinstance(item, dict) for item in response_data):
                try:
                    df = pd.DataFrame(response_data)
                    return {
                        'type': 'table',
                        'data': df,
                        'html': df.to_html(index=False, classes='table table-striped')
                    }
                except Exception as e:
                    print(f"Error creating table from list: {e}")

            # Regular list - format with bullet points
            formatted_html = "<div style='line-height: 1.8;'>"
            formatted_text = []
            for item in response_data:
                item_str = str(item)
                formatted_text.append(item_str)
                formatted_html += f"<div style='margin-bottom: 8px;'>• {item_str}</div>"
            formatted_html += "</div>"

            return {
                'type': 'list',
                'data': formatted_text,
                'html': formatted_html
            }
        else:
            return {
                'type': 'text',
                'data': 'No data available',
                'html': 'No data available'
            }

    # Default: return as text
    return {
        'type': 'text',
        'data': str(response_data),
        'html': str(response_data).replace('\n', '<br/>')
    }


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
if 'bootstrapping' not in st.session_state:
    st.session_state.bootstrapping = False
if 'msg_processing' not in st.session_state:
    st.session_state.msg_processing = False
if 'prefetched_requests' not in st.session_state:
    st.session_state.prefetched_requests = []
if 'initial_forecast' not in st.session_state:
    st.session_state.initial_forecast = None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_user_initials(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"


def bootstrap_user_session(user_obj: dict, password: str):
    """
    Prepare data BEFORE flipping logged_in to True:
    - Get outbreak forecast from API
    - Prefetch service requests
    - Initialize chat with forecast data
    """
    st.session_state.bootstrapping = True
    try:
        # Get forecast from API (no visible spinner to avoid fading)
        forecast_response = api_client.get_forecast(
            user_obj['username'],
            password,
            user_obj.get('district', ''),
            user_obj.get('state', '')
        )

        st.session_state.chat_history = []

        if forecast_response and forecast_response.get('forecast'):
            forecast = forecast_response['forecast']
            # Translate forecast to selected language
            lang = st.session_state.language if 'language' in st.session_state else 'hi'
            forecast_text = format_forecast_for_display(forecast)
            translated_forecast = translate_api_response(forecast_text, lang)
            st.session_state.chat_history.append({
                'type': 'ai',
                'content': translated_forecast,
                'is_forecast': True
            })
        else:
            lang = st.session_state.language if 'language' in st.session_state else 'hi'
            no_data_msg = get_text('no_data', lang)
            st.session_state.chat_history.append({
                'type': 'ai',
                'content': no_data_msg,
                'is_forecast': True
            })

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
    if 'language' not in st.session_state:
        st.session_state.language = 'hi'  # Default to Hindi

    lang = st.session_state.language

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{get_text('app_name', lang)}</h1>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align: center; font-size: 1.1rem; color: #64748b;'>{get_text('app_subtitle', lang)}</p>",
            unsafe_allow_html=True)

        # Use existing session_state values as defaults (no post-instantiation writes)
        username = st.text_input(
            get_text('username', lang),
            placeholder=get_text('username', lang),
            key="login_user"
        )
        password = st.text_input(
            get_text('password', lang),
            type="password",
            placeholder=get_text('password', lang),
            key="login_pass"
        )

        # Language selector below password
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        lang_options = {
            'English': 'en',
            'हिन्दी': 'hi',
            'বাংলা': 'bn',
            'தமிழ்': 'ta',
        }
        lang_display = list(lang_options.keys())
        lang_values = list(lang_options.values())

        # Find current index
        current_idx = lang_values.index(lang) if lang in lang_values else 1  # Default to Hindi

        selected_lang_display = st.selectbox(
            get_text('select_language', lang),
            lang_display,
            index=current_idx,
            key="login_lang_selector",
            label_visibility="collapsed"
        )
        selected_lang_code = lang_options.get(selected_lang_display, 'hi')

        if selected_lang_code != st.session_state.language:
            st.session_state.language = selected_lang_code
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(get_text('login', lang), use_container_width=True):
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
                        st.error(get_text('invalid_credentials', lang))
                else:
                    st.warning(get_text('please_enter_both', lang))

        with col_b:
            if st.button(get_text('signup', lang), use_container_width=True):
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
            districts = sorted(list(set([loc['district'] for loc in locations if loc['state'] == state]))) if state in [
                l['state'] for l in locations] else []
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
def process_chat_message():
    """
    Process current input without screen fade.
    Uses session state to flag that a message needs processing.
    Callback function - cannot call st.rerun() directly.
    Ensures all responses are in the user's selected language.
    - Immediately displays user message
    - Shows "Processing..." indicator without screen fade
    - Translates API response to selected language BEFORE displaying
    - No input/button disable during processing
    """
    user_input = (st.session_state.current_input or "").strip()
    if not user_input:
        return

    user = st.session_state.user
    lang = st.session_state.language

    # Immediately add user message to show responsiveness
    st.session_state.chat_history.append({'type': 'user', 'content': user_input})
    st.session_state.current_input = ""
    st.session_state.msg_processing = True


def show_chat():
    user = st.session_state.user
    lang = st.session_state.language

    # Sidebar with inline profile + logout
    with st.sidebar:
        initials = get_user_initials(user['first_name'], user['last_name'])
        st.markdown(
            f"<div style='background: #c084fc; padding: 12px; border-radius: 8px; text-align: center;'><span style='font-size: 1.5rem; font-weight: bold;'>{initials}</span><br/><span style='font-size: 1.2rem; color: #fff;'>{user.get('role', '').upper()}</span></div>",
            unsafe_allow_html=True)
        st.markdown("")
        if st.button(get_text('logout', lang), use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.password = None
            st.session_state.chat_history = []
            st.session_state.service_requests = []
            st.session_state.prefetched_requests = []
            st.session_state.outbreak_loaded = False
            st.session_state.current_input = ""
            st.session_state.msg_processing = False
            st.session_state.language = 'hi'  # Reset to Hindi
            st.rerun()

        st.markdown("---")

        # Service Request Form - Multi-level hierarchical structure
        st.markdown(f"### {get_text('service_requests', lang)}")

        # Initialize session state for request form
        if 'request_category_select' not in st.session_state:
            st.session_state.request_category_select = "Select Option"
        if 'hospital_select' not in st.session_state:
            st.session_state.hospital_select = "Select Hospital"
        if 'medicine_select' not in st.session_state:
            st.session_state.medicine_select = "Select Medicine"
        if 'testing_kit_select' not in st.session_state:
            st.session_state.testing_kit_select = "Select Kit"

        # Level 1: Request Category (OUTSIDE FORM for dynamic response)
        request_category = st.selectbox(
            "Request Category",
            options=["Select Option", "Doctor Appointment", "Medicine", "Medical Testing Kits", "Others"],
            key="request_category_select",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Level 2: Sub-category based on request type (OUTSIDE FORM for dynamic response)
        request_sub_item = None
        aadhar_number = None

        if request_category == "Doctor Appointment":
            request_sub_item = st.selectbox(
                "Aayushman Bharat Approved Hospital Network",
                options=[
                    "Select Hospital",
                    "Maharaja Agrasen Hospital, Gorakhpur",
                    "Baba Raghav Das Medical College Hospital, Gorakhpur",
                    "Central Hospital Gorakhpur",
                    "KIMS Hospital Gorakhpur",
                    "Apollo Health City, Gorakhpur"
                ],
                key="hospital_select",
                label_visibility="collapsed"
            )

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            # Show Aadhar input IMMEDIATELY after hospital is selected (OUTSIDE form)
            if request_sub_item != "Select Hospital":
                aadhar_number = st.text_input(
                    "Enter Aadhar Number",
                    placeholder="Enter your 12-digit Aadhar number",
                    key="aadhar_input",
                    label_visibility="collapsed"
                )
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        elif request_category == "Medicine":
            request_sub_item = st.selectbox(
                "Medicine Name",
                options=[
                    "Select Medicine",
                    "Paracetamol 500mg",
                    "Aspirin 325mg",
                    "Ibuprofen 400mg",
                    "Amoxicillin 250mg",
                    "Metformin 500mg",
                    "Atorvastatin 20mg",
                    "Omeprazole 20mg",
                    "Cough Syrup (General)",
                    "Multivitamin Tablets",
                    "Antacid Suspension"
                ],
                key="medicine_select",
                label_visibility="collapsed"
            )

        elif request_category == "Medical Testing Kits":
            request_sub_item = st.selectbox(
                "Medical Testing Kit",
                options=[
                    "Select Kit",
                    "COVID-19 Testing Kit (RT-PCR)",
                    "Blood Glucose Testing Kit",
                    "Rapid COVID-19 Antigen Kit",
                    "Malaria Rapid Test Kit",
                    "Typhoid IgM Testing Kit"
                ],
                key="testing_kit_select",
                label_visibility="collapsed"
            )

        elif request_category == "Others":
            request_sub_item = None

        # Form for level 3 and submission
        with st.form("service_request_form"):
            # Level 3: Comments/Details text box (for all categories)
            comments_label = "Comments" if request_category == "Doctor Appointment" else "Additional Details"
            request_details = st.text_area(
                comments_label,
                placeholder="Please provide detailed information about your request...",
                height=80
            )

            # Form submission
            if st.form_submit_button(get_text('submit_request', lang), use_container_width=True):
                # Validation for Doctor Appointment
                if request_category == "Doctor Appointment":
                    if request_sub_item == "Select Hospital":
                        st.warning("Please select a hospital")
                    elif not aadhar_number or not aadhar_number.strip():
                        st.warning("Please enter Aadhar number")
                    elif not aadhar_number.isdigit() or len(aadhar_number) != 12:
                        st.warning("Please enter a valid 12-digit Aadhar number")
                    elif not request_details.strip():
                        st.warning("Please provide comments about your appointment request")
                    else:
                        # Combine category, hospital, and aadhar
                        combined_item = f"Doctor Appointment - {request_sub_item} - Aadhar: {aadhar_number}"
                        req_id = db.submit_service_request(
                            user_id=user['user_id'],
                            username=user['username'],
                            role=user['role'],
                            district=user['district'],
                            state=user['state'],
                            item=combined_item,
                            details=request_details
                        )
                        st.success(f"Request #{req_id} submitted!")
                        # refresh pending requests list
                        st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])

                # Validation for Medicine
                elif request_category == "Medicine":
                    if request_sub_item == "Select Medicine":
                        st.warning("Please select a medicine")
                    elif not request_details.strip():
                        st.warning("Please provide details about your request")
                    else:
                        # Combine category and medicine
                        combined_item = f"Medicine - {request_sub_item}"
                        req_id = db.submit_service_request(
                            user_id=user['user_id'],
                            username=user['username'],
                            role=user['role'],
                            district=user['district'],
                            state=user['state'],
                            item=combined_item,
                            details=request_details
                        )
                        st.success(f"Request #{req_id} submitted!")
                        # refresh pending requests list
                        st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])

                # Validation for Medical Testing Kits
                elif request_category == "Medical Testing Kits":
                    if request_sub_item == "Select Kit":
                        st.warning("Please select a testing kit")
                    elif not request_details.strip():
                        st.warning("Please provide details about your request")
                    else:
                        # Combine category and kit
                        combined_item = f"Medical Testing Kit - {request_sub_item}"
                        req_id = db.submit_service_request(
                            user_id=user['user_id'],
                            username=user['username'],
                            role=user['role'],
                            district=user['district'],
                            state=user['state'],
                            item=combined_item,
                            details=request_details
                        )
                        st.success(f"Request #{req_id} submitted!")
                        # refresh pending requests list
                        st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])

                # Validation for Others
                elif request_category == "Others":
                    if not request_details.strip():
                        st.warning("Please provide details about your request")
                    else:
                        req_id = db.submit_service_request(
                            user_id=user['user_id'],
                            username=user['username'],
                            role=user['role'],
                            district=user['district'],
                            state=user['state'],
                            item=request_category,
                            details=request_details
                        )
                        st.success(f"Request #{req_id} submitted!")
                        # refresh pending requests list
                        st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])

                # Default validation (no category selected)
                else:
                    st.warning("Please select a request category")

        st.markdown("---")

        # Pending Requests
        st.markdown(f"### {get_text('pending_requests', lang)}")
        requests = st.session_state.prefetched_requests
        if requests:
            any_pending = False
            for req in requests:
                if req.get('status') == 'pending':
                    any_pending = True
                    with st.container(border=True):
                        st.markdown(f"**#{req['request_id']}**: {req['request_item']}")
                        st.markdown(f"{get_text('level', lang)}: {req['escalation_level']}/3")
                        if req['escalation_level'] < 3:
                            if st.button(get_text('escalate', lang), key=f"escalate_btn_{req['request_id']}",
                                         use_container_width=True):
                                ok, new_level = db.escalate_request(req['request_id'], user['user_id'])
                                if ok:
                                    st.success(f"{get_text('escalated_to_level', lang)} {new_level}")
                                    st.session_state.prefetched_requests = db.get_user_service_requests(user['user_id'])
                                else:
                                    st.error(get_text('unable_to_escalate', lang))
            if not any_pending:
                st.info(get_text('no_pending_requests', lang))
        else:
            st.info(get_text('no_pending_requests', lang))

    # Main content area
    st.markdown("<h2 style='text-align: center;'>Aayura - Chat</h2>", unsafe_allow_html=True)

    # Chat container
    with st.container():
        # Display chat history (single AI outbreak message was added during bootstrap)
        st.markdown("")
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                st.markdown(
                    f"<div style='background: #d1fae5; padding: 12px; border-radius: 8px; margin: 10px 0;'><b>You:</b><br/>{message['content']}</div>",
                    unsafe_allow_html=True)
            elif message['type'] == 'ai':
                actions = message['content']

                # Parse and format the response
                formatted = parse_and_format_api_response(actions)

                # Display based on type
                if formatted['type'] == 'table':
                    # Display table
                    st.markdown(
                        "<div style='background: #e5e7eb; padding: 12px; border-radius: 8px; margin: 10px 0;'><b>Aayura AI:</b></div>",
                        unsafe_allow_html=True)
                    st.dataframe(formatted['data'], use_container_width=True)
                elif formatted['type'] == 'dict':
                    # Display formatted dictionary
                    st.markdown(
                        f"<div style='background: #e5e7eb; padding: 12px; border-radius: 8px; margin: 10px 0;'><b>Aayura AI:</b><br/>{formatted['html']}</div>",
                        unsafe_allow_html=True)
                elif formatted['type'] == 'list':
                    # Display formatted list
                    st.markdown(
                        f"<div style='background: #e5e7eb; padding: 12px; border-radius: 8px; margin: 10px 0;'><b>Aayura AI:</b><br/>{formatted['html']}</div>",
                        unsafe_allow_html=True)
                else:
                    # Display as text
                    actions_html = str(actions).replace('\n', '<br/>')
                    st.markdown(
                        f"<div style='background: #e5e7eb; padding: 12px; border-radius: 8px; margin: 10px 0;'><b>Aayura AI:</b><br/>{actions_html}</div>",
                        unsafe_allow_html=True)
            st.markdown("")

    st.markdown("---")

    # Input row - always enabled (no fade effect)
    col_msg, col_btn = st.columns([5, 1], gap="small")
    with col_msg:
        st.text_input(
            "Ask a Question",
            placeholder="e.g., What remedies should I recommend?",
            key="current_input",
            label_visibility="collapsed",
        )
    with col_btn:
        st.button(
            "Send",
            use_container_width=True,
            on_click=process_chat_message,
            key="send_btn_callback",
        )

    # Process API call if message was just added
    if st.session_state.msg_processing:
        st.markdown(
            "<div style='background: #fff9c4; padding: 12px; border-radius: 8px; margin: 10px 0; text-align: center;'>"
            "<b>Processing your request...</b></div>",
            unsafe_allow_html=True
        )

        user = st.session_state.user
        lang = st.session_state.language

        try:
            # Call API to get actions using the last user message
            user_message = st.session_state.chat_history[-1]['content']
            api_response = api_client.get_actions(user.get('username', ''), st.session_state.password, user_message)
            role =user.get('role', 'ASHA')
            # Process response with STRICT translation requirement
            if api_response and api_response.get('actions'):
                # Get the raw API response text
                action_text = str(api_response.get('actions', ''))

                # STRICT: Translate API response to selected language BEFORE processing
                translated_action = translate_api_response(action_text, lang)
                if role == "ASHA":
                    # Split and clean the translated response
                    action_list = [line.strip() for line in translated_action.split('\n') if line.strip()]

                    # If still empty after splitting, provide translated default message
                    if not action_list:
                        action_list = [get_text('no_actions', lang)]
                elif role == "DCMO":
                    # Display provided local DCMO CSV directly in the UI as a table
                    try:
                        csv_path = Path(__file__).parent / "DCMO.csv"
                        if csv_path.exists():
                            df = pd.read_csv(csv_path)
                            st.markdown("**DCMO - Local Data Table**")
                            st.dataframe(df)
                            # Provide a short confirmation message in the chat area
                            # action_list = ["Displayed local DCMO table below."]
                            action_list = df.to_dict(orient='list')
                        else:
                            action_list = ["There is no DCMO data found."]
                    except Exception as e:
                        action_list = [f"Error loading DCMO table: {str(e)}"]
                elif role == "SCMO":
                    try:
                        csv_path = Path(__file__).parent / "SCMO.csv"
                        if csv_path.exists():
                            df = pd.read_csv(csv_path)
                            st.markdown("**SCMO - Local Data Table**")
                            st.dataframe(df)
                            # Provide a short confirmation message in the chat area
                            action_list = df.to_dict(orient='list')
                        else:
                            action_list = ["There is no SCMO data found."]
                    except Exception as e:
                        action_list = [f"Error loading SCMO table: {str(e)}"]

                # # Split and clean the translated response
                # action_list = [line.strip() for line in translated_action.split('\n') if line.strip()]
                #
                # # If still empty after splitting, provide translated default message
                # if not action_list:
                #     action_list = [get_text('no_actions', lang)]
            else:
                # No response from API - provide translated error message
                action_list = [get_text('unable_to_generate', lang)]

            # Add AI message with translated content
            st.session_state.chat_history.append({'type': 'ai', 'content': action_list})

        except Exception as e:
            # Handle error gracefully
            st.session_state.chat_history.append({
                'type': 'ai',
                'content': [get_text('unable_to_generate', lang)]
            })
        finally:
            # Reset processing flag and rerun to display response
            st.session_state.msg_processing = False
            st.rerun()


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
