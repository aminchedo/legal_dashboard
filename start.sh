#!/bin/bash

# Start script for Legal Dashboard
# Suitable for Hugging Face Spaces and Docker environments

echo "🚀 Starting Legal Dashboard..."

# Set default environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
export DATABASE_DIR=${DATABASE_DIR:-/app/data}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/data /app/cache /app/logs /app/uploads /app/backups /tmp/app_fallback

# Set permissions if possible (ignore errors)
chmod -R 755 /app/data /app/cache /app/logs /app/uploads /app/backups 2>/dev/null || true
chmod -R 777 /tmp/app_fallback 2>/dev/null || true

# Function to check if port is available
check_port() {
    local port=${1:-8000}
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to wait for dependencies
wait_for_deps() {
    echo "⏳ Checking dependencies..."
    
    # Check if we can create database
    python3 -c "
import sqlite3
import os
db_path = os.environ.get('DATABASE_DIR', '/app/data') + '/test.db'
try:
    conn = sqlite3.connect(db_path)
    conn.close()
    os.remove(db_path)
    print('✅ Database access OK')
except Exception as e:
    print(f'⚠️  Database access issue: {e}')
" || echo "Database check completed with warnings"
}

# Check environment
echo "🔍 Environment check..."
echo "  - Python: $(python3 --version)"
echo "  - Working directory: $(pwd)"
echo "  - Database dir: $DATABASE_DIR"
echo "  - User: $(whoami)"
echo "  - UID: $(id -u)"

# Wait for dependencies
wait_for_deps

# Check port availability
PORT=${PORT:-8000}
if ! check_port $PORT; then
    echo "🔄 Trying alternative port..."
    PORT=$((PORT + 1))
    check_port $PORT || PORT=7860  # HF Spaces default
fi

echo "🌐 Using port: $PORT"

# Health check function
health_check() {
    local max_attempts=30
    local attempt=1
    
    echo "🏥 Starting health check..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -fs http://localhost:$PORT/health >/dev/null 2>&1; then
            echo "✅ Application is healthy!"
            return 0
        fi
        
        echo "⏳ Health check attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Start application
echo "🎯 Starting application on port $PORT..."

# For Hugging Face Spaces
if [ "$SPACE_ID" != "" ]; then
    echo "🤗 Running in Hugging Face Spaces environment"
    
    # Use gradio or fastapi depending on setup
    if [ -f "app.py" ]; then
        echo "📱 Starting with Gradio interface..."
        python3 app.py
    else
        echo "🚀 Starting FastAPI server..."
        uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
    fi
else
    # Standard Docker/local environment
    echo "🐳 Running in standard environment"
    
    # Start with uvicorn
    if command -v uvicorn >/dev/null 2>&1; then
        echo "🚀 Starting with uvicorn..."
        uvicorn app.main:app \
            --host 0.0.0.0 \
            --port $PORT \
            --workers 1 \
            --access-log \
            --log-level info &
        
        # Store PID
        APP_PID=$!
        echo "📝 Application PID: $APP_PID"
        
        # Wait a bit then check health
        sleep 5
        if health_check; then
            echo "🎉 Application started successfully!"
            wait $APP_PID
        else
            echo "💥 Application failed to start properly"
            kill $APP_PID 2>/dev/null
            exit 1
        fi
    else
        echo "❌ uvicorn not found, trying with python..."
        python3 -c "
import uvicorn
uvicorn.run('app.main:app', host='0.0.0.0', port=$PORT, workers=1)
        "
    fi
fi