# 🚀 Legal Dashboard - Deployment Checklist

## ✅ Pre-Deployment Validation

### System Components Status
- [x] **Main Application** (`app/main.py`) - Enhanced with service integration
- [x] **HF Spaces Entry Point** (`app.py`) - Production ready
- [x] **Dependencies** (`requirements.txt`) - Complete and optimized
- [x] **Documentation** (README.md, API.md, DEPLOYMENT.md) - Comprehensive
- [x] **Rating Service** - Enhanced with `get_unrated_items()` method
- [x] **Background Tasks** - Automatic scraping and rating implemented
- [x] **Persian Language Support** - Complete implementation
- [x] **API Endpoints** - All new endpoints implemented

### Validation Results
- [x] **File Structure**: ✅ PASSED
- [x] **Main Integration**: ✅ PASSED  
- [x] **HF Spaces Compatibility**: ✅ PASSED
- [x] **Requirements Completeness**: ✅ PASSED
- [x] **Documentation Completeness**: ✅ PASSED
- [x] **Rating Service**: ✅ PASSED

**Overall Validation Score: 100% PASSED**

## 🎯 Deployment Options

### Option 1: Hugging Face Spaces (Recommended)

#### Step 1: Create Space
- [ ] Go to [Hugging Face Spaces](https://huggingface.co/spaces)
- [ ] Click "Create new Space"
- [ ] Choose settings:
  - **Owner**: Your username
  - **Space name**: `legal-dashboard`
  - **License**: MIT
  - **SDK**: Gradio
  - **Space hardware**: CPU (Basic)

#### Step 2: Upload Files
```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/legal-dashboard
cd legal-dashboard

# Copy all project files
cp -r /path/to/legal-dashboard/* .

# Add files to git
git add .
git commit -m "Initial deployment of Legal Dashboard"
git push
```

#### Step 3: Configure Environment Variables
In Space settings, add:
```bash
# Core settings
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=7860

# Security
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_DIR=/tmp/legal_dashboard/data
TRANSFORMERS_CACHE=/tmp/cache
HF_HOME=/tmp/cache

# Scraping
SCRAPING_DELAY=2.0
SCRAPING_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=5

# Rating
RATING_BATCH_SIZE=10
RATING_CONFIDENCE_THRESHOLD=0.7
```

#### Step 4: Verify Deployment
- [ ] Check Space is running
- [ ] Test health endpoint: `https://YOUR_USERNAME-legal-dashboard.hf.space/api/health`
- [ ] Verify API documentation: `https://YOUR_USERNAME-legal-dashboard.hf.space/docs`

### Option 2: Docker Deployment

#### Step 1: Build Image
```bash
# Build Docker image
docker build -t legal-dashboard:latest .

# Test locally
docker run -p 8000:8000 legal-dashboard:latest
```

#### Step 2: Deploy with Docker Compose
```bash
# Create docker-compose.yml
version: '3.8'
services:
  legal-dashboard:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_DIR=/app/data
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
    restart: unless-stopped

# Deploy
docker-compose up -d
```

### Option 3: Local Development

#### Step 1: Setup Environment
```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

#### Step 3: Run Application
```bash
# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or run with Gradio
python app.py
```

## 🔍 Post-Deployment Verification

### Health Check
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "scraping": "healthy", 
    "rating": "healthy",
    "background_tasks": "running"
  }
}
```

### System Status Check
```bash
# Check system status
curl http://localhost:8000/api/system/status

# Expected response:
{
  "system": {
    "status": "operational",
    "version": "1.0.0"
  },
  "scraping": {
    "active_jobs": 0,
    "background_running": true
  },
  "rating": {
    "total_rated": 0,
    "background_running": true
  }
}
```

### API Documentation
- [ ] Verify Swagger UI: `http://localhost:8000/docs`
- [ ] Verify ReDoc: `http://localhost:8000/redoc`
- [ ] Test key endpoints:
  - [ ] `GET /api/health`
  - [ ] `GET /api/system/status`
  - [ ] `POST /api/system/start-scraping`
  - [ ] `POST /api/system/start-rating`

## 📊 Performance Monitoring

### Key Metrics to Monitor
- [ ] **API Response Time**: < 2 seconds
- [ ] **Memory Usage**: < 1GB
- [ ] **Scraping Success Rate**: > 50 documents/day
- [ ] **Rating Accuracy**: > 85%
- [ ] **System Uptime**: > 99%

### Monitoring Endpoints
- [ ] `/api/health` - Basic health check
- [ ] `/api/system/status` - System status
- [ ] `/api/system/statistics` - Performance metrics
- [ ] `/api/scraping/statistics` - Scraping metrics
- [ ] `/api/rating/summary` - Rating summary

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

#### 2. Database Connection Issues
```bash
# Check database directory permissions
ls -la /app/data/

# Create database directory if missing
mkdir -p /app/data
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. Port Conflicts
```bash
# Check if port is in use
netstat -tulpn | grep :8000

# Change port in .env file
PORT=8001
```

### Log Files
- [ ] Application logs: `/tmp/legal_dashboard.log`
- [ ] System logs: `docker logs legal-dashboard`
- [ ] Error logs: Check console output

## 🔧 Maintenance

### Regular Tasks
- [ ] **Daily**: Check system health
- [ ] **Weekly**: Review scraping statistics
- [ ] **Monthly**: Update dependencies
- [ ] **Quarterly**: Database optimization

### Backup Strategy
- [ ] Database backup: `sqlite3 legal_documents.db ".backup backup.db"`
- [ ] Configuration backup: Copy `.env` file
- [ ] Log rotation: Implement log rotation

### Updates
- [ ] Monitor for dependency updates
- [ ] Test updates in development environment
- [ ] Deploy updates during maintenance window
- [ ] Verify system health after updates

## 📞 Support

### Documentation
- [ ] **README.md**: Complete system overview
- [ ] **API.md**: API documentation
- [ ] **DEPLOYMENT.md**: Deployment guide
- [ ] **IMPLEMENTATION_SUMMARY.md**: Implementation details

### Contact Information
- [ ] GitHub Issues: For bug reports
- [ ] GitHub Discussions: For questions
- [ ] Email: For direct support

### Resources
- [ ] FastAPI Documentation: https://fastapi.tiangolo.com/
- [ ] Hugging Face Spaces: https://huggingface.co/docs/hub/spaces
- [ ] Docker Documentation: https://docs.docker.com/

---

## ✅ Final Checklist

### Before Deployment
- [x] All components implemented and tested
- [x] Validation passed (100%)
- [x] Documentation complete
- [x] Dependencies updated
- [x] Environment variables configured

### After Deployment
- [ ] Health check passes
- [ ] API endpoints respond correctly
- [ ] Background tasks start automatically
- [ ] Persian language support works
- [ ] Documentation accessible
- [ ] Monitoring setup complete

### Production Readiness
- [x] **Code Quality**: Production ready
- [x] **Security**: JWT authentication, input validation
- [x] **Performance**: Optimized for HF Spaces
- [x] **Scalability**: Background processing, caching
- [x] **Monitoring**: Health checks, metrics
- [x] **Documentation**: Comprehensive guides

---

**🏛️ Legal Dashboard** - Ready for Production Deployment

**Status**: ✅ **DEPLOYMENT READY**
**Validation**: ✅ **100% PASSED**
**Next Step**: Deploy to Hugging Face Spaces