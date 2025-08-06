# Legal Dashboard - AI Document Processing System

A production-ready FastAPI application for processing and analyzing legal documents with AI-powered insights.

## 🚀 Features

- **Document Upload**: Support for PDF and TXT files
- **Text Extraction**: Automatic text extraction from PDF documents
- **AI Analysis**: Document analysis with language detection and legal term identification
- **Real-time Dashboard**: Live system status and document processing reports
- **Responsive UI**: Modern, mobile-friendly interface built with Tailwind CSS
- **Health Monitoring**: Built-in health checks and system status monitoring

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn server
- **Database**: SQLite with automatic initialization
- **File Processing**: PyPDF2 for PDF text extraction
- **API Endpoints**: RESTful API with comprehensive error handling

### Frontend (HTML/CSS/JS)
- **Styling**: Tailwind CSS for responsive design
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome for UI elements
- **Real-time Updates**: Fetch API for dynamic content

## 📋 Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- PyPDF2
- SQLite3

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legal-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the dashboard**
   - Open http://localhost:8000
   - API docs: http://localhost:8000/api/docs

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t legal-dashboard .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 legal-dashboard
   ```

### Hugging Face Spaces Deployment

1. **Create a new Space**
   - Go to https://huggingface.co/spaces
   - Create a new Space with "Docker" SDK

2. **Upload the code**
   - Upload all project files to your Space
   - The application will automatically deploy

3. **Access your Space**
   - Your dashboard will be available at your Space URL
   - Example: `https://your-username-legal-dashboard.hf.space`

## 📁 Project Structure

```
legal-dashboard/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API modules (optional)
│   ├── models/              # Data models (optional)
│   └── services/            # Business logic (optional)
├── frontend/
│   └── index.html           # Main dashboard interface
├── data/                    # Database and uploaded files
├── app.py                   # Entry point for HF Spaces
├── start.sh                 # Startup script
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Main dashboard interface
- `GET /api/health` - System health check
- `POST /api/upload` - Upload and process documents
- `GET /api/reports` - Get processed reports
- `DELETE /api/clear` - Clear all data

### Health Check Response
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "uploads": "healthy",
    "api": "healthy"
  },
  "version": "1.0.0"
}
```

### Upload Response
```json
{
  "filename": "document.pdf",
  "status": "success",
  "message": "Document uploaded and processed successfully"
}
```

## 🎯 Key Features

### Document Processing
- **PDF Support**: Extract text from PDF files using PyPDF2
- **TXT Support**: Direct text file processing
- **Analysis**: Automatic document analysis including:
  - Word count and sentence count
  - Language detection (Persian/English)
  - Legal term identification
  - Document type classification

### Dashboard Features
- **Real-time Status**: Live system health monitoring
- **Upload Progress**: Visual progress indicators
- **Report Management**: View and manage processed documents
- **Analytics**: Document statistics and charts
- **Responsive Design**: Works on desktop and mobile

### System Features
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Structured logging for debugging
- **Health Checks**: Built-in health monitoring
- **Graceful Fallbacks**: System continues working even if optional services fail

## 🔒 Security Features

- **File Validation**: Strict file type checking
- **Size Limits**: Configurable file size limits
- **Error Sanitization**: Safe error message handling
- **CORS Configuration**: Proper CORS setup for web access

## 🚀 Performance Optimizations

- **Async Processing**: Non-blocking file uploads
- **Database Optimization**: Efficient SQLite queries
- **Caching**: Optional Redis caching support
- **Compression**: GZip middleware for faster responses
- **Worker Configuration**: Single worker for Hugging Face Spaces compatibility

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or use a different port
   PORT=8001 python app.py
   ```

2. **Permission errors**
   ```bash
   # Ensure proper permissions
   chmod +x start.sh
   sudo chown -R $USER:$USER /app/data
   ```

3. **Database errors**
   ```bash
   # Reset database
   rm -rf /app/data/legal_dashboard.db
   # Restart application
   ```

### Logs

Check application logs for detailed error information:
```bash
# View logs
tail -f /app/logs/app.log

# Check health endpoint
curl http://localhost:8000/api/health
```

## 🔄 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Application port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `production` | Environment mode |
| `DATABASE_DIR` | `/app/data` | Database directory |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at `/api/docs`
- Check the health endpoint at `/api/health`

## 🎉 Deployment Status

- ✅ Local development
- ✅ Docker deployment
- ✅ Hugging Face Spaces
- ✅ Production ready
- ✅ Error handling
- ✅ Health monitoring
- ✅ Responsive UI
- ✅ Document processing
- ✅ Real-time updates

---

**Legal Dashboard** - Making legal document processing simple and efficient! 🏛️