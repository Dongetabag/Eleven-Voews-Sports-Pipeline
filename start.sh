#!/bin/bash
# Quick start script for Eleven Views Opportunity Engine

echo "🚀 Eleven Views Opportunity Engine - Quick Start"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from template..."
    cp .env.template .env
    echo "✅ .env created. Please add your API keys!"
    echo ""
    echo "Required keys:"
    echo "  - APIFY_API_TOKEN"
    echo "  - GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter to continue after adding keys, or Ctrl+C to exit..."
fi

# Install dependencies if needed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt --quiet
    echo "✅ Dependencies installed"
    echo ""
fi

# Create directories
mkdir -p data logs cache exports backups
echo "✅ Directories created"
echo ""

# Run pre-flight checks
echo "🔍 Running pre-flight checks..."
python3 launch.py --check-only 2>/dev/null || python3 -c "
from utils.logger import get_logger
from database import Database
logger = get_logger('startup')
try:
    db = Database()
    logger.info('✅ Database initialized')
    print('✅ Pre-flight checks passed')
except Exception as e:
    print(f'⚠️  Warning: {e}')
"
echo ""

# Start the system
echo "🌐 Starting dashboard..."
echo "   Dashboard: http://localhost:5000"
echo "   API: http://localhost:5000/api/v1"
echo "   Health: http://localhost:5000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 launch.py



