# Legal Dashboard OCR - Deployment Instructions

## 🚀 Quick Start

### 1. Local Development Setup

```bash
# Clone or navigate to the project
cd legal_dashboard_ocr

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HF_TOKEN="your_huggingface_token"

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Application

- **Web Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📦 Project Structure

```
legal_dashboard_ocr/
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── test_structure.py           # Structure verification
├── DEPLOYMENT_INSTRUCTIONS.md  # This file
├── app/                        # Backend application
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── documents.py        # Document CRUD
│   │   ├── ocr.py             # OCR processing
│   │   └── dashboard.py       # Dashboard analytics
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── ocr_service.py     # OCR pipeline
│   │   ├── database_service.py # Database operations
│   │   └── ai_service.py      # AI scoring
│   └── models/                 # Data models
│       ├── __init__.py
│       └── document_models.py  # Pydantic schemas
├── frontend/                   # Web interface
│   ├── improved_legal_dashboard.html
│   └── test_integration.html
├── tests/                      # Test suite
│   ├── test_api_endpoints.py
│   └── test_ocr_pipeline.py
├── data/                       # Sample documents
│   └── sample_persian.pdf
└── huggingface_space/          # HF Space deployment
    ├── app.py                  # Gradio interface
    ├── Spacefile               # Deployment config
    └── README.md               # Space documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Hugging Face Token (required for OCR models)
HF_TOKEN=your_huggingface_token_here

# Database configuration (optional)
DATABASE_URL=sqlite:///legal_documents.db

# Server configuration (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Add it to your environment variables

## 🧪 Testing

### Run Structure Test
```bash
python test_structure.py
```

### Run API Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
python -m pytest tests/
```

### Manual Testing
```bash
# Test OCR endpoint
curl -X POST "http://localhost:8000/api/ocr/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/sample_persian.pdf"

# Test dashboard
curl "http://localhost:8000/api/dashboard/summary"
```

## 🚀 Deployment Options

### 1. Hugging Face Spaces

#### Automatic Deployment
1. Create a new Space on Hugging Face
2. Upload all files from `huggingface_space/` directory
3. Set the `HF_TOKEN` environment variable in Space settings
4. The Space will automatically build and deploy

#### Manual Deployment
```bash
# Navigate to HF Space directory
cd huggingface_space

# Install dependencies
pip install -r ../requirements.txt

# Run the Gradio app
python app.py
```

### 2. Docker Deployment

#### Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t legal-dashboard-ocr .

# Run container
docker run -p 8000:8000 \
  -e HF_TOKEN=your_token \
  legal-dashboard-ocr
```

### 3. Production Deployment

#### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### Using Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the correct directory
cd legal_dashboard_ocr

# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 2. OCR Model Loading Issues
```bash
# Check HF token
echo $HF_TOKEN

# Test model download
python -c "from transformers import pipeline; p = pipeline('image-to-text', 'microsoft/trocr-base-stage1')"
```

#### 3. Database Issues
```bash
# Check database file
ls -la legal_documents.db

# Reset database (if needed)
rm legal_documents.db
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Performance Optimization

#### 1. Model Caching
```python
# In app/services/ocr_service.py
# Models are automatically cached by Hugging Face
# Cache location: ~/.cache/huggingface/
```

#### 2. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
```

#### 3. Memory Management
```python
# In app/main.py
# Configure memory limits
import gc
gc.collect()  # Force garbage collection
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Logs
```bash
# View application logs
tail -f logs/app.log

# View error logs
grep ERROR logs/app.log
```

## 🔒 Security

### Production Checklist
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Secure file upload validation
- [ ] Regular security updates

### Environment Security
```bash
# Secure environment variables
export HF_TOKEN="your_secure_token"
export DATABASE_URL="your_secure_db_url"

# Use .env file (don't commit to git)
echo "HF_TOKEN=your_token" > .env
echo ".env" >> .gitignore
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Run multiple instances
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
uvicorn app.main:app --host 0.0.0.0 --port 8002 &
```

### Load Balancing
```nginx
upstream legal_dashboard {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://legal_dashboard;
    }
}
```

## 🆘 Support

### Getting Help
1. Check the logs for error messages
2. Verify environment variables are set
3. Test with the sample PDF in `data/`
4. Check the API documentation at `/docs`

### Common Commands
```bash
# Start development server
uvicorn app.main:app --reload

# Run tests
python -m pytest tests/

# Check structure
python test_structure.py

# View API docs
open http://localhost:8000/docs
```

## 🎯 Next Steps

1. **Deploy to Hugging Face Spaces** for easy sharing
2. **Add authentication** for production use
3. **Implement user management** for multi-user support
4. **Add more OCR models** for different document types
5. **Create mobile app** for document scanning
6. **Add batch processing** for multiple documents
7. **Implement advanced analytics** and reporting

---

**Note**: This project is designed for Persian legal documents. Ensure your documents are clear and well-scanned for best OCR results. 