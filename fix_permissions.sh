#!/bin/bash

# Fix Permissions Script for Legal Dashboard
# This script resolves common permission issues

echo "🔧 Legal Dashboard - Permission Fix Script"
echo "=========================================="

# Function to create directory with fallback
create_dir_with_fallback() {
    local dir_path=$1
    local fallback_path=$2
    
    echo "📁 Creating directory: $dir_path"
    
    if mkdir -p "$dir_path" 2>/dev/null && [ -w "$dir_path" ]; then
        echo "✅ Successfully created: $dir_path"
        return 0
    else
        echo "⚠️  Failed to create $dir_path, trying fallback: $fallback_path"
        if mkdir -p "$fallback_path" 2>/dev/null && [ -w "$fallback_path" ]; then
            echo "✅ Successfully created fallback: $fallback_path"
            return 0
        else
            echo "❌ Failed to create both primary and fallback directories"
            return 1
        fi
    fi
}

# Check current user and permissions
echo ""
echo "🔍 System Information:"
echo "  - Current user: $(whoami)"
echo "  - User ID: $(id -u)"
echo "  - Group ID: $(id -g)"
echo "  - Working directory: $(pwd)"
echo "  - Home directory: $HOME"

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "  - Environment: Docker Container"
    IN_DOCKER=true
else
    echo "  - Environment: Host System"
    IN_DOCKER=false
fi

# Check if running in HF Spaces
if [ "$SPACE_ID" != "" ]; then
    echo "  - Platform: Hugging Face Spaces"
    IN_HF_SPACES=true
else
    echo "  - Platform: Standard"
    IN_HF_SPACES=false
fi

echo ""
echo "🏗️ Creating necessary directories..."

# Create directories with fallbacks
if [ "$IN_HF_SPACES" = true ]; then
    # HF Spaces specific paths
    create_dir_with_fallback "/tmp/legal_dashboard/data" "$HOME/legal_dashboard/data"
    create_dir_with_fallback "/tmp/legal_dashboard/cache" "$HOME/legal_dashboard/cache"
    create_dir_with_fallback "/tmp/legal_dashboard/logs" "$HOME/legal_dashboard/logs"
    create_dir_with_fallback "/tmp/legal_dashboard/uploads" "$HOME/legal_dashboard/uploads"
    
    # Set environment variables for HF Spaces
    export DATABASE_DIR="/tmp/legal_dashboard/data"
    export TRANSFORMERS_CACHE="/tmp/legal_dashboard/cache"
    export HF_HOME="/tmp/legal_dashboard/cache"
    
    echo "✅ HF Spaces directories configured"
    
elif [ "$IN_DOCKER" = true ]; then
    # Docker specific paths
    create_dir_with_fallback "/app/data" "/tmp/app_data"
    create_dir_with_fallback "/app/database" "/tmp/app_database"
    create_dir_with_fallback "/app/cache" "/tmp/app_cache"
    create_dir_with_fallback "/app/logs" "/tmp/app_logs"
    create_dir_with_fallback "/app/uploads" "/tmp/app_uploads"
    create_dir_with_fallback "/app/backups" "/tmp/app_backups"
    
    echo "✅ Docker directories configured"
    
else
    # Host system paths
    create_dir_with_fallback "./data" "$HOME/legal_dashboard/data"
    create_dir_with_fallback "./cache" "$HOME/legal_dashboard/cache"
    create_dir_with_fallback "./logs" "$HOME/legal_dashboard/logs"
    create_dir_with_fallback "./uploads" "$HOME/legal_dashboard/uploads"
    create_dir_with_fallback "./backups" "$HOME/legal_dashboard/backups"
    
    echo "✅ Host system directories configured"
fi

# Set permissions where possible
echo ""
echo "🔒 Setting permissions..."

# Function to set permissions safely
safe_chmod() {
    local path=$1
    local perm=$2
    
    if [ -d "$path" ] && [ -w "$path" ]; then
        chmod $perm "$path" 2>/dev/null && echo "  ✅ Set $perm on $path" || echo "  ⚠️  Could not set permissions on $path"
    fi
}

# Apply permissions to existing directories
for dir in "/app/data" "/app/database" "/app/cache" "/app/logs" "/app/uploads" "/app/backups" \
           "/tmp/legal_dashboard" "/tmp/app_data" "/tmp/app_database" "/tmp/app_cache" \
           "$HOME/legal_dashboard" "./data" "./cache" "./logs" "./uploads" "./backups"; do
    safe_chmod "$dir" 755
done

# Test database creation
echo ""
echo "🗄️ Testing database creation..."

test_db_creation() {
    local test_dir=$1
    local test_db="$test_dir/test.db"
    
    if [ -d "$test_dir" ] && [ -w "$test_dir" ]; then
        if python3 -c "
import sqlite3
import os
try:
    conn = sqlite3.connect('$test_db')
    conn.execute('CREATE TABLE test (id INTEGER)')
    conn.close()
    os.remove('$test_db')
    print('✅ Database test successful in $test_dir')
    exit(0)
except Exception as e:
    print('❌ Database test failed in $test_dir: {}'.format(e))
    exit(1)
" 2>/dev/null; then
            echo "$test_dir"  # Return the working directory
            return 0
        fi
    fi
    return 1
}

# Find working database directory
WORKING_DB_DIR=""
for test_dir in "/app/data" "/tmp/legal_dashboard/data" "/tmp/app_data" "$HOME/legal_dashboard/data" "./data"; do
    if test_db_creation "$test_dir"; then
        WORKING_DB_DIR="$test_dir"
        break
    fi
done

if [ "$WORKING_DB_DIR" != "" ]; then
    echo "✅ Database directory confirmed: $WORKING_DB_DIR"
    export DATABASE_DIR="$WORKING_DB_DIR"
else
    echo "⚠️  No writable database directory found, will use in-memory database"
    export DATABASE_DIR=":memory:"
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️ Creating environment configuration..."

ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << EOF
# Auto-generated environment configuration
DATABASE_DIR=$DATABASE_DIR
DATABASE_NAME=legal_documents.db
JWT_SECRET_KEY=your-secret-key-change-in-production-$(date +%s)
LOG_LEVEL=INFO
ENVIRONMENT=production
PYTHONPATH=/app
PYTHONUNBUFFERED=1
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
EOF
    echo "✅ Created $ENV_FILE"
else
    echo "✅ $ENV_FILE already exists"
fi

# Test Python imports
echo ""
echo "🐍 Testing Python dependencies..."

python3 -c "
try:
    import fastapi
    import uvicorn
    import sqlite3
    import os
    print('✅ Core dependencies available')
except ImportError as e:
    print('❌ Missing dependency: {}'.format(e))
    
try:
    import gradio
    print('✅ Gradio available')
except ImportError:
    print('⚠️  Gradio not available (ok if not using HF Spaces)')
" 2>/dev/null

# Final status
echo ""
echo "📊 Final Status:"
echo "  - Database directory: ${DATABASE_DIR:-Not set}"
echo "  - Cache directory: ${TRANSFORMERS_CACHE:-Not set}"
echo "  - Log level: ${LOG_LEVEL:-INFO}"
echo "  - Environment: ${ENVIRONMENT:-development}"

# Instructions
echo ""
echo "🚀 Next Steps:"
echo "  1. Run the application:"
if [ "$IN_HF_SPACES" = true ]; then
    echo "     python app.py"
elif [ "$IN_DOCKER" = true ]; then
    echo "     ./start.sh"
    echo "     # or"
    echo "     uvicorn app.main:app --host 0.0.0.0 --port 8000"
else
    echo "     ./start.sh"
    echo "     # or"
    echo "     python app.py"
    echo "     # or"
    echo "     uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

echo ""
echo "  2. Default login credentials:"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "  3. Change default password after first login!"

echo ""
echo "🎉 Permission fix completed!"
echo "============================================"