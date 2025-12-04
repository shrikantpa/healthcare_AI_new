#!/usr/bin/env python3
"""
Script to reinitialize the user_mapping table
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def reinitialize_user_mapping():
    """Drop and recreate user_mapping table with default admin user"""
    print("🔄 Reinitializing user_mapping table...")
    
    db_manager = DatabaseManager()
    
    # Drop the user_mapping table
    print("\n1️⃣ Dropping user_mapping table...")
    db_manager.drop_user_mapping_table()
    
    # Create tables (which will recreate user_mapping)
    print("\n2️⃣ Creating user_mapping table...")
    db_manager.create_tables()
    
    # Add default admin user
    print("\n3️⃣ Adding default admin user...")
    db_manager.add_default_users()
    
    # Verify the admin user was created
    print("\n4️⃣ Verifying admin user...")
    db_manager.cursor.execute('SELECT user_id, username, password, role FROM user_mapping')
    users = db_manager.cursor.fetchall()
    
    print("\n" + "="*60)
    print("✅ USER_MAPPING TABLE REINITIALIZED SUCCESSFULLY")
    print("="*60)
    print("\nUser records in user_mapping table:")
    for user in users:
        print(f"  - ID: {user[0]}, Username: {user[1]}, Password: {user[2]}, Role: {user[3]}")
    
    print("\n" + "="*60)
    print("🔐 LOGIN CREDENTIALS:")
    print("="*60)
    print("  Username: admin")
    print("  Password: admin123")
    print("  Role: ASHA")
    print("="*60)
    
    db_manager.close()
    print("\n✓ Database reinitialized successfully!\n")

if __name__ == "__main__":
    reinitialize_user_mapping()
