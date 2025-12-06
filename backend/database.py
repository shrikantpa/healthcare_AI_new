"""
Database module for managing SQLite database operations
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "MALERIA.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_connection()
        
    def init_connection(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.row_factory = sqlite3.Row
        
    def drop_user_mapping_table(self):
        """Drop the user_mapping table completely"""
        try:
            self.cursor.execute('DROP TABLE IF EXISTS user_mapping')
            self.conn.commit()
            print("✓ user_mapping table dropped successfully")
        except Exception as e:
            print(f"❌ Error dropping user_mapping table: {str(e)}")
    
    def create_tables(self):
        """Create all required tables"""
        # Location table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                UNIQUE(state, district)
            )
        ''')
        
        # Malaria State Data table
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
        
        # User Mapping table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_mapping (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer'
            )
        ''')
        
        # Users table (for signup)
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
                role TEXT ,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES location(location_id),
                UNIQUE(username)
            )
        ''')
        
        # Service Requests table
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
        print("✓ All tables created successfully")
        
    def load_json_data(self, json_path: str):
        """Load data from JSON file into database"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"Loading {len(data)} records from {json_path}...")
        counter = 0
        for record in data:
            counter+=1
            state = record.get('state', 'Unknown')
            district = record.get('district', 'Unknown')

            # Check if location already exists
            self.cursor.execute(
                '''
                SELECT location_id FROM location WHERE state = ? AND district = ?
                ''',
                (state, district)
            )
            location = self.cursor.fetchone()
            if not location:
                self.cursor.execute(
                    '''
                    INSERT INTO location (state, district)
                    VALUES (?, ?)
                    ''',
                    (state, district)
                )

                # Fetch the newly created location_id
                self.cursor.execute(
                    '''
                    SELECT location_id FROM location WHERE state = ? AND district = ?
                    ''',
                    (state, district)
                )
                location = self.cursor.fetchone()
            location_id = location[0]
            if location_id:
                try:
                    self.cursor.execute(
                        '''
                        INSERT INTO malaria_state_data 
                        (location_id, year, cases_examined, cases_detected, 
                         male_case_examined, female_case_examined, 
                         male_case_detected, female_case_detected)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            location_id,
                            record.get('year', 0),
                            record.get('cases_examined', 0),
                            record.get('cases_detected', 0),
                            record.get('male_case_examined', 0),
                            record.get('female_case_examined', 0),
                            record.get('male_case_detected', 0),
                            record.get('female_case_detected', 0)
                        )
                    )
                except sqlite3.IntegrityError:
                    print(f"Duplicate entry found: {record}")

        self.conn.commit()
        print(f"Counter: {counter} Data loaded successfully")
        
    def add_default_users(self):
        """Add default admin user to user table"""
        try:
            # Check if admin user already exists
            self.cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
            existing_admin = self.cursor.fetchone()
            if not existing_admin:
                location_id = self.verify_location('Gorakhpur', 'Uttar Pradesh')
                self.cursor.execute('''
                    INSERT INTO users (first_name, last_name, username, password, district, state, location_id, role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', ('Bhuwan','Thada','bhuwan','bt12345','Gorakhpur', 'Uttar Pradesh', location_id,'ASHA'))
                self.conn.commit()
                print("✓ Default user added: username=Bhuwan, role=ASHA")
                location_id = self.verify_location('Gorakhpur', 'Uttar Pradesh')
                self.cursor.execute('''
                                    INSERT INTO users (first_name, last_name, username, password, district, state, location_id, role)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                'Shyam', 'Mishra', 'shyam', 'shyam12345', 'Gorakhpur', 'Uttar Pradesh', location_id, 'DCMO'))
                self.conn.commit()
                print("✓ Default user added: username=Shyam, role=DCMO")
                location_id = self.verify_location('Gorakhpur', 'Uttar Pradesh')
                self.cursor.execute('''INSERT INTO users (first_name, last_name, username, password, district, state, location_id, role)
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                                ''', (
                    'Amit', 'Gupta', 'amit', 'amit12345', 'Gorakhpur', 'Uttar Pradesh', location_id, 'SCMO'))
                self.conn.commit()
                print("✓ Default user added: username=Amit, role=SCMO")

            else:
                print("✓ Default user already exists in users table")
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Admin user already exists: {str(e)}")
        
    def get_district_data(self, district: str, state: Optional[str] = None) -> Dict:
        """Get malaria data for a specific district"""
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
        
        # Format the data
        result = {
            'district': district,
            'state': rows[0][0] if rows else None,
            'years': []
        }
        
        for row in rows:
            result['years'].append({
                'year': row[2],
                'cases_examined': row[3],
                'cases_detected': row[4],
                'male_case_examined': row[5],
                'female_case_examined': row[6],
                'male_case_detected': row[7],
                'female_case_detected': row[8]
            })
        
        return result
    
    def get_all_districts(self) -> List[Dict]:
        """Get all districts and states"""
        self.cursor.execute('SELECT DISTINCT state, district FROM location ORDER BY state, district')
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            result.append({
                'state': row[0],
                'district': row[1]
            })
        
        return result
    
    def verify_location(self, district: str, state: str) -> Optional[int]:
        """
        Verify if district and state combination exists in location table
        
        Args:
            district: District name
            state: State name
            
        Returns:
            location_id if found, None otherwise
        """
        self.cursor.execute('''
            SELECT location_id FROM location 
            WHERE district = ? AND state = ?
        ''', (district, state))
        
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def create_user(self, first_name: str, last_name: str, username: str, 
                   password: str, district: str, state: str, role: str = 'analyst') -> Optional[Dict]:
        """
        Create a new user after verifying location
        
        Args:
            first_name: User's first name
            last_name: User's last name
            username: Username for login
            password: User's password
            district: District name (must exist in location table)
            state: State name (must match with district)
            role: User role (ASHA, DCMO, SCMO, or analyst)
            
        Returns:
            Dict with user details if successful, None if location not found
        """
        # Verify location
        location_id = self.verify_location(district, state)
        
        if not location_id:
            return None
        
        # Create user
        try:
            self.cursor.execute('''
                INSERT INTO users 
                (first_name, last_name, username, password, district, state, location_id, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, username, password, district, state, location_id, role))
            
            self.conn.commit()
            
            # Return user details
            self.cursor.execute('''
                SELECT user_id, first_name, last_name, username, district, state, role, created_at
                FROM users WHERE username = ?
            ''', (username,))
            
            user = self.cursor.fetchone()
            return {
                'user_id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'username': user[3],
                'district': user[4],
                'state': user[5],
                'role': user[6],
                'created_at': user[7]
            }
        except sqlite3.IntegrityError as e:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user details by username"""
        self.cursor.execute('''
            SELECT user_id, first_name, last_name, username, district, state, role
            FROM users WHERE username = ?
        ''', (username,))
        
        user = self.cursor.fetchone()
        if not user:
            return None
        
        return {
            'user_id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'username': user[3],
            'district': user[4],
            'state': user[5],
            'role': user[6]
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
