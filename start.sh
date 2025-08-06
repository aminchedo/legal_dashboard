#!/bin/bash

# Legal Dashboard Startup Script for Hugging Face Spaces
# =====================================================

set -e

echo "🚀 Starting Legal Dashboard..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/data /app/cache /app/logs /app/uploads

# Set proper permissions
chmod -R 755 /app

# Check if we're in Hugging Face Spaces environment
if [ -n "$SPACE_ID" ]; then
    echo "🌐 Running in Hugging Face Spaces environment"
    PORT=${PORT:-8000}
else
    echo "🏠 Running in local environment"
    PORT=${PORT:-8000}
fi

echo "🔧 Environment: $ENVIRONMENT"
echo "🌐 Port: $PORT"
echo "📊 Log Level: $LOG_LEVEL"

# Start the application
echo "🎯 Starting FastAPI application..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level $LOG_LEVEL \
    --access-log