#!/usr/bin/env python3
"""
Script to drop and recreate users table with fresh data
"""

import sys
import sqlite3
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.database import DatabaseManager

def main():
    db = DatabaseManager()
    
    print("=" * 60)
    print("REINITIALIZING USERS TABLE")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Drop users table if exists
        print("\n1. Dropping users table...")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        print("   ✓ Users table dropped")
        
    except Exception as e:
        print(f"   ✗ Error dropping table: {e}")
        return False
    finally:
        conn.close()
    
    # Recreate tables
    print("\n2. Recreating tables...")
    try:
        db.create_tables()
        print("   ✓ Tables recreated successfully")
    except Exception as e:
        print(f"   ✗ Error recreating tables: {e}")
        return False
    
    # Add location entry for Rajasthan, Jaipur if not exists
    print("\n3. Ensuring location entries exist...")
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        locations = [
            ("Rajasthan", "Jaipur"),
            ("Uttar Pradesh", "Etah")
        ]
        
        for state, district in locations:
            cursor.execute(
                "SELECT location_id FROM location WHERE state = ? AND district = ?",
                (state, district)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO location (state, district) VALUES (?, ?)",
                    (state, district)
                )
                print(f"   ✓ Added location: {state} - {district}")
            else:
                print(f"   ✓ Location exists: {state} - {district}")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"   ✗ Error managing locations: {e}")
        return False
    
    # User data to insert
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
    
    print("\n4. Inserting user records...")
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        for user in users_data:
            username = user["username"]
            state = user["state"]
            district = user["district"]
            
            # Get location_id
            cursor.execute(
                "SELECT location_id FROM location WHERE state = ? AND district = ?",
                (state, district)
            )
            location_result = cursor.fetchone()
            
            if not location_result:
                print(f"   ✗ Location not found for {state} - {district}")
                continue
            
            location_id = location_result[0]
            
            # Insert user
            cursor.execute(
                """INSERT INTO users 
                   (first_name, last_name, username, password, state, district, location_id, role)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user["first_name"], user["last_name"], user["username"],
                 user["password"], user["state"], user["district"], location_id, user["role"])
            )
            print(f"   ✓ Inserted user: {username} ({user['first_name']} {user['last_name']}) - {user['role']}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"   ✗ Error inserting users: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("USERS TABLE REINITIALIZATION COMPLETED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
