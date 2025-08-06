# 📊 Legal Dashboard - داشبورد حقوقی

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-Latest-orange.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive legal document management and analysis system built with FastAPI and Gradio, optimized for multiple deployment environments including Hugging Face Spaces.

## 🌟 Features

- **📄 Document Management**: Upload, process, and manage legal documents (PDF, DOCX, DOC, TXT)
- **🤖 AI-Powered Analysis**: Extract key information using advanced NLP models
- **🔐 Secure Authentication**: JWT-based authentication with role management
- **📊 Analytics Dashboard**: Real-time analytics and document insights
- **🌐 Web Scraping**: Extract content from legal websites
- **🔍 Smart Search**: Advanced search capabilities across documents
- **📱 Multi-Interface**: Web dashboard + Gradio interface for HF Spaces
- **🌍 Multi-Language**: Persian/Farsi and English support
- **☁️ Multi-Platform**: Docker, HF Spaces, Local deployment

## 🚀 Quick Start

### Option 1: Hugging Face Spaces (Recommended for Demo)

1. **Fork this Space** or create a new one
2. **Upload all files** to your space
3. **Set environment variables** in Space settings:
   ```bash
   JWT_SECRET_KEY=your-super-secret-key-here
   DATABASE_DIR=/tmp/legal_dashboard/data
   LOG_LEVEL=INFO
   ```
4. **Launch the space** - it will automatically start

**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

### Option 2: Docker Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd legal-dashboard

# Build and run
docker-compose up --build

# Or with Docker only
docker build -t legal-dashboard .
docker run -p 8000:8000 legal-dashboard
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run application
python run.py
# Or specific interfaces:
python app.py          # Gradio interface
uvicorn app.main:app   # FastAPI only
```

## 📁 Project Structure

```
legal-dashboard/
├── 🚀 Deployment & Config
│   ├── run.py                  # Universal runner (All environments)
│   ├── config.py               # Configuration management
│   ├── startup_hf.py           # HF Spaces startup
│   ├── app.py                  # Gradio interface
│   ├── Dockerfile              # Docker configuration
│   ├── docker-compose.yml      # Docker Compose
│   ├── requirements.txt        # Dependencies
│   └── .env                    # Environment variables
│
├── 🏗️ Backend (FastAPI)
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── api/                # API endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── documents.py    # Document management
│   │   │   ├── analytics.py    # Analytics
│   │   │   ├── scraping.py     # Web scraping
│   │   │   └── ...
│   │   ├── services/           # Business logic
│   │   │   ├── ai_service.py   # AI/ML services
│   │   │   ├── database_service.py
│   │   │   ├── ocr_service.py  # OCR processing
│   │   │   └── ...
│   │   └── models/             # Data models
│
├── 🎨 Frontend
│   ├── index.html              # Main dashboard
│   ├── documents.html          # Document management
│   ├── analytics.html          # Analytics page
│   ├── upload.html             # File upload
│   ├── js/                     # JavaScript modules
│   └── ...
│
└── 🧪 Testing & Docs
    ├── tests/                  # Test suites
    ├── docs/                   # Documentation
    └── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | `auto-generated` | JWT signing key |
| `DATABASE_DIR` | `/app/data` | Database directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `production` | Environment type |
| `HF_HOME` | `/app/cache` | ML models cache |
| `PORT` | `8000/7860` | Server port |
| `WORKERS` | `1/4` | Worker processes |

### Multi-Environment Support

The system automatically detects and optimizes for:

- **🤗 Hugging Face Spaces**: Gradio interface, optimized resources
- **🐳 Docker**: Full FastAPI with all features
- **💻 Local**: Development mode with hot reload

## 🔧 Advanced Configuration

### Custom Model Configuration

```python
# config.py - AI Configuration
ai_config = {
    "model_name": "microsoft/trocr-small-stage1",  # HF Spaces
    "device": "cpu",  # Force CPU for compatibility
    "max_workers": 1,  # Optimize for environment
    "batch_size": 1,   # Memory optimization
}
```

### Database Optimization

```python
# Automatic fallback paths for different environments
database_paths = [
    "/app/data/legal_documents.db",      # Docker
    "/tmp/legal_dashboard/data/legal.db", # HF Spaces
    "./data/legal_documents.db",         # Local
    ":memory:"                           # Final fallback
]
```

## 🐛 Troubleshooting

### Common Issues & Solutions

1. **Permission Denied Error**
   ```bash
   PermissionError: [Errno 13] Permission denied: '/app/database'
   ```
   **Solution**: System uses automatic fallback directories
   ```bash
   # Check logs for actual directory used:
   grep "📁.*directory" logs/legal_dashboard.log
   ```

2. **bcrypt Version Error**
   ```bash
   (trapped) error reading bcrypt version
   ```
   **Solution**: Fixed with bcrypt==4.0.1 in requirements.txt

3. **Redis Connection Failed**
   ```bash
   Redis connection failed: Error 111 connecting to localhost:6379
   ```
   **Solution**: System automatically falls back to in-memory storage

4. **Model Loading Issues**
   ```bash
   OutOfMemoryError or CUDA errors
   ```
   **Solution**: System forces CPU mode and optimizes model selection

5. **Port Already in Use**
   ```bash
   [Errno 48] Address already in use
   ```
   **Solution**: System automatically tries alternative ports

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run.py

# Or check specific components
python -c "from config import config; print(config.get_summary())"
```

### Health Checks

```bash
# Check system health
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "ocr": "healthy",
    "ai": "healthy"
  }
}
```

## 🔒 Security

### Authentication Flow

1. **Registration**: Create account with email/password
2. **Login**: JWT access token (30 min) + refresh token (7 days)
3. **Authorization**: Role-based access control (admin/user)
4. **Session Management**: Secure token storage and refresh

### Security Features

- 🔐 bcrypt password hashing
- 🎫 JWT token authentication
- 🛡️ CORS protection
- 📝 Audit logging
- 🔒 Role-based permissions
- 🚫 Rate limiting (planned)

### Default Credentials

⚠️ **Change immediately in production:**
- Username: `admin`
- Password: `admin123`

## 📊 API Documentation

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | User authentication |
| `/api/auth/register` | POST | User registration |
| `/api/documents` | GET/POST | Document management |
| `/api/ocr/process` | POST | OCR processing |
| `/api/analytics/overview` | GET | Analytics data |
| `/api/scraping/scrape` | POST | Web scraping |
| `/api/health` | GET | System health |

### Interactive Documentation

- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI JSON**: `/api/openapi.json`

## 🚀 Deployment Guide

### Hugging Face Spaces

1. **Create Space**:
   ```bash
   # Go to https://huggingface.co/spaces
   # Create new Space with Gradio SDK
   ```

2. **Upload Files**:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
   cp -r legal-dashboard/* YOUR_SPACE/
   cd YOUR_SPACE
   git add .
   git commit -m "Initial deployment"
   git push
   ```

3. **Configure Space**:
   - Set `JWT_SECRET_KEY` in Space settings
   - Optional: Set custom domain

### Docker Production

```bash
# Production docker-compose
version: "3.8"
services:
  legal-dashboard:
    build: .
    ports:
      - "80:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Kubernetes (Advanced)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legal-dashboard
  template:
    spec:
      containers:
      - name: legal-dashboard
        image: legal-dashboard:latest
        ports:
        - containerPort: 8000
        env:
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: legal-dashboard-secrets
              key: jwt-secret
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Run tests**: `python -m pytest tests/`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Create Pull Request**

### Development Setup

```bash
# Clone and setup
git clone <repo-url>
cd legal-dashboard

# Install development dependencies
pip install -r requirements.txt
pip install pytest black isort mypy

# Setup pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/ -v

# Code formatting
black .
isort .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework
- **Gradio**: Easy-to-use ML app interface  
- **Hugging Face**: Model hosting and Spaces platform
- **Transformers**: State-of-the-art NLP models
- **Chart.js**: Beautiful charts and visualizations

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Email**: Contact maintainers
- **Documentation**: [Full Docs](./docs/)

---

### 🌐 Live Demo

Try the live demo: [Your HF Space URL]

**Made with ❤️ for the legal community**