#!/bin/bash
# Quick Start Script for Healthcare Data Analytics API

echo "🏥 Healthcare Data Analytics - Malaria Outbreak Forecasting API"
echo "================================================================"

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if venv exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    cd ..
    python -m venv venv
    cd backend
fi

# Activate venv
echo "✓ Activating virtual environment..."
source ../venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r ../requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "
import sys
sys.path.insert(0, '..')
from backend.database import DatabaseManager
db = DatabaseManager()
db.create_tables()
db.cursor.execute('SELECT COUNT(*) FROM malaria_state_data')
count = db.cursor.fetchone()[0]
if count == 0:
    db.load_json_data('../data/maleria_data.json')
db.add_default_users()
db.close()
print('✓ Database ready')
"

# Start API
echo ""
echo "🚀 Starting FastAPI Server..."
echo "📍 API Available at: http://localhost:8000"
echo "📚 Docs at: http://localhost:8000/docs"
echo "🔐 Default Users:"
echo "   - admin / admin123 (role: admin)"
echo "   - user / user123 (role: viewer)"
echo "   - analyst / analyst123 (role: analyst)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================================"

python main.py
