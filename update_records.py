#!/usr/bin/env python3
"""
Script to update location and user records in the database
"""

import sys
import sqlite3
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.database import DatabaseManager

def main():
    db = DatabaseManager()
    db.create_tables()  # Initialize tables first
    
    print("=" * 60)
    print("UPDATING DATABASE RECORDS")
    print("=" * 60)
    
    # Add location entry for Rajasthan, Jaipur
    print("\n1. Adding location entry: Rajasthan - Jaipur")
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute(
            "SELECT * FROM location WHERE state = ? AND district = ?",
            ("Rajasthan", "Jaipur")
        )
        
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO location (state, district) VALUES (?, ?)",
                ("Rajasthan", "Jaipur")
            )
            conn.commit()
            print("   ✓ Location added: Rajasthan - Jaipur")
        else:
            print("   ✓ Location already exists: Rajasthan - Jaipur")
        
        conn.close()
    except Exception as e:
        print(f"   ✗ Error adding location: {e}")
        return False
    
    # User data to insert/update
    users_data = [
        {
            "first_name": "Sheetal",
            "last_name": "Devi",
            "username": "sheetal",
            "password": "sheetal123",
            "state": "Rajasthan",
            "district": "Jaipur",
            "role": "ASHA"
        },
        {
            "first_name": "Seeta",
            "last_name": "Devi",
            "username": "seeta",
            "password": "seeta123",
            "state": "Uttar Pradesh",
            "district": "Etah",
            "role": "ASHA"
        },
        {
            "first_name": "Rahul",
            "last_name": "Gupta",
            "username": "rahul",
            "password": "rahul123",
            "state": "Uttar Pradesh",
            "district": "Etah",
            "role": "DCMO"
        },
        {
            "first_name": "Akshita",
            "last_name": "Mishra",
            "username": "akshita",
            "password": "akshita123",
            "state": "Uttar Pradesh",
            "district": "Etah",
            "role": "SCMO"
        }
    ]
    
    print("\n2. Updating/Inserting user records")
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        for user in users_data:
            username = user["username"]
            state = user["state"]
            district = user["district"]
            
            # Get location_id for the user's state and district
            cursor.execute(
                "SELECT location_id FROM location WHERE state = ? AND district = ?",
                (state, district)
            )
            location_result = cursor.fetchone()
            
            if not location_result:
                print(f"   ✗ Location not found for {state} - {district}")
                continue
            
            location_id = location_result[0]
            
            # Check if user exists
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing user
                cursor.execute(
                    """UPDATE users SET 
                       first_name = ?, last_name = ?, password = ?, 
                       state = ?, district = ?, location_id = ?, role = ?
                       WHERE username = ?""",
                    (user["first_name"], user["last_name"], user["password"],
                     user["state"], user["district"], location_id, user["role"], username)
                )
                print(f"   ✓ Updated user: {username} ({user['first_name']} {user['last_name']})")
            else:
                # Insert new user
                cursor.execute(
                    """INSERT INTO users 
                       (first_name, last_name, username, password, state, district, location_id, role)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user["first_name"], user["last_name"], user["username"],
                     user["password"], user["state"], user["district"], location_id, user["role"])
                )
                print(f"   ✓ Inserted user: {username} ({user['first_name']} {user['last_name']})")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"   ✗ Error updating users: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("DATABASE UPDATE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    # Display updated records
    print("\nVerifying records:")
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        print("\nLocations:")
        cursor.execute("SELECT state, district FROM location ORDER BY state, district")
        for row in cursor.fetchall():
            print(f"   • {row[0]} - {row[1]}")
        
        print("\nUsers:")
        cursor.execute("""
            SELECT username, first_name, last_name, role, district, state 
            FROM users 
            ORDER BY username
        """)
        for row in cursor.fetchall():
            print(f"   • {row[0]}: {row[1]} {row[2]} ({row[3]}) - {row[4]}, {row[5]}")
        
        conn.close()
    except Exception as e:
        print(f"Error verifying records: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
