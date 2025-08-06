# Docker Container Fixes Summary

## Issues Identified

1. **Database Connection Error**: `sqlite3.OperationalError: unable to open database file`
2. **OCR Model Loading Error**: Incompatible model `microsoft/trocr-base-handwritten`
3. **Container Startup Failure**: Database initialization during module import

## Fixes Applied

### 1. Database Service Improvements

**File**: `app/services/database_service.py`

**Changes**:
- Removed automatic database initialization during import
- Added explicit `initialize()` method that must be called
- Improved directory creation with proper permissions (777)
- Added fallback to current directory if `/app/data` fails
- Added environment variable support for database path

**Key Changes**:
```python
def __init__(self, db_path: str = None):
    # Use environment variable or default path
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', '/app/data/legal_dashboard.db')
    
    self.db_path = db_path
    self.connection = None
    
    # Ensure data directory exists with proper permissions
    self._ensure_data_directory()
    
    # Don't initialize immediately - let it be called explicitly
    logger.info(f"Database manager initialized with path: {self.db_path}")
```

### 2. OCR Service Improvements

**File**: `app/services/ocr_service.py`

**Changes**:
- Added multiple compatible model fallbacks
- Improved error handling for model loading
- Added graceful degradation to basic text extraction
- Removed problematic model `microsoft/trocr-base-handwritten`

**Compatible Models**:
1. `microsoft/trocr-base-stage1`
2. `microsoft/trocr-base-handwritten`
3. `microsoft/trocr-small-stage1`
4. `microsoft/trocr-small-handwritten`

### 3. Docker Configuration Improvements

**File**: `Dockerfile`

**Changes**:
- Added `curl` for health checks
- Added environment variable for database path
- Added startup script for proper initialization
- Ensured proper permissions on data directory

**Key Additions**:
```dockerfile
ENV DATABASE_PATH=/app/data/legal_dashboard.db
RUN chmod +x start.sh
CMD ["./start.sh"]
```

### 4. Startup Script

**File**: `start.sh`

**Purpose**: Ensures proper directory creation and permissions before starting the application

```bash
#!/bin/bash
# Create data and cache directories if they don't exist
mkdir -p /app/data /app/cache
# Set proper permissions
chmod -R 777 /app/data /app/cache
# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 7860
```

### 5. Docker Compose Configuration

**File**: `docker-compose.yml`

**Changes**:
- Added proper volume mounts for data persistence
- Added environment variables
- Added health check configuration
- Improved service naming

### 6. Debug and Testing Tools

**Files Created**:
- `debug_container.py` - Tests container environment
- `test_db_connection.py` - Tests database connectivity
- `rebuild_and_test.sh` - Automated rebuild script (Linux/Mac)
- `rebuild_and_test.ps1` - Automated rebuild script (Windows)

### 7. Documentation

**File**: `DEPLOYMENT_GUIDE.md`

**Content**:
- Comprehensive troubleshooting guide
- Step-by-step deployment instructions
- Common issues and solutions
- Environment variable documentation

## Testing the Fixes

### Quick Test Commands

1. **Test Database Connection**:
   ```bash
   docker run --rm legal-dashboard-ocr python debug_container.py
   ```

2. **Rebuild and Test** (Windows):
   ```powershell
   .\rebuild_and_test.ps1
   ```

3. **Rebuild and Test** (Linux/Mac):
   ```bash
   ./rebuild_and_test.sh
   ```

4. **Manual Docker Compose**:
   ```bash
   docker-compose up --build
   ```

## Expected Results

After applying these fixes:

1. ✅ **Container starts successfully** without database errors
2. ✅ **OCR models load properly** with fallback support
3. ✅ **Database is accessible** and persistent across restarts
4. ✅ **Health endpoint responds** correctly
5. ✅ **Application is accessible** at `http://localhost:7860`

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_PATH` | `/app/data/legal_dashboard.db` | SQLite database location |
| `TRANSFORMERS_CACHE` | `/app/cache` | Hugging Face model cache |
| `HF_HOME` | `/app/cache` | Hugging Face home directory |
| `HF_TOKEN` | (not set) | Hugging Face authentication |

## Volume Mounts

- `./data:/app/data` - Database and uploaded files
- `./cache:/app/cache` - Hugging Face model cache

## Next Steps

1. **Test the application** using the provided scripts
2. **Monitor logs** for any remaining issues
3. **Deploy to production** if testing is successful
4. **Add authentication** for production use
5. **Implement monitoring** for long-term stability

## Support

If issues persist:
1. Check container logs: `docker logs <container_name>`
2. Run debug script: `docker exec -it <container> python debug_container.py`
3. Verify Docker resources (memory, disk space)
4. Check network connectivity for model downloads 