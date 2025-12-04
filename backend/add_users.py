"""
Script to add test users to the database
"""
from database import DatabaseManager

def main():
    # Initialize database manager
    db = DatabaseManager('malaria_data.db')
    
    # Define users to add
    users = [
        {
            'first_name': 'Seeta',
            'last_name': 'Devi',
            'username': 'seeta',
            'password': '123456',
            'district': 'Etah',
            'state': 'Uttar Pradesh',
            'role': 'ASHA'
        },
        {
            'first_name': 'Rahul',
            'last_name': 'Gupta',
            'username': 'rahul',
            'password': '123456',
            'district': 'Etah',
            'state': 'Uttar Pradesh',
            'role': 'DCMO'
        },
        {
            'first_name': 'Akshita',
            'last_name': 'Mishra',
            'username': 'akshita',
            'password': '123456',
            'district': 'Etah',
            'state': 'Uttar Pradesh',
            'role': 'SCMO'
        }
    ]
    
    # Insert users
    for user in users:
        result = db.create_user(
            first_name=user['first_name'],
            last_name=user['last_name'],
            username=user['username'],
            password=user['password'],
            district=user['district'],
            state=user['state'],
            role=user['role']
        )
        
        if result:
            print(f"✓ User created: {user['first_name']} {user['last_name']} ({user['username']}) - Role: {user['role']}")
        else:
            print(f"❌ Failed to create user: {user['username']}")
    
    # Add to user_mapping table as well (for login)
    for user in users:
        try:
            db.cursor.execute('''
                INSERT INTO user_mapping (username, password, role)
                VALUES (?, ?, ?)
            ''', (user['username'], user['password'], user['role']))
            db.conn.commit()
            print(f"✓ Added {user['username']} to user_mapping table")
        except Exception as e:
            print(f"⚠️ {user['username']} already in user_mapping: {str(e)}")
    
    # Close connection
    db.close()
    print("\n✓ All users inserted successfully!")

if __name__ == '__main__':
    main()
