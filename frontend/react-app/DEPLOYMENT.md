# Iranian Legal Archive System - Frontend Deployment Guide

## 🚀 Quick Start

### Development Server
```bash
npm run dev
```
Access at: http://localhost:3000

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build Docker image manually
docker build -t iranian-legal-archive-frontend .
docker run -p 3000:3000 iranian-legal-archive-frontend
```

## 📋 Deployment Options

### 1. Traditional Web Server (Nginx/Apache)

#### Using the deployment script:
```bash
./deploy.sh
```

#### Manual deployment:
```bash
# Build the application
npm run build

# Copy to web server
sudo cp -r dist/* /var/www/iranian-legal-archive/

# Set permissions
sudo chown -R www-data:www-data /var/www/iranian-legal-archive/
sudo chmod -R 755 /var/www/iranian-legal-archive/
```

### 2. Docker Deployment

#### Single Container:
```bash
docker build -t iranian-legal-archive-frontend .
docker run -d -p 3000:3000 --name frontend iranian-legal-archive-frontend
```

#### With Docker Compose (Recommended):
```bash
docker-compose up -d
```

### 3. Cloud Deployment

#### Vercel:
```bash
npm install -g vercel
vercel --prod
```

#### Netlify:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### AWS S3 + CloudFront:
```bash
aws s3 sync dist/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key variables:
- `VITE_API_URL`: Backend API URL
- `VITE_WS_URL`: WebSocket URL
- `VITE_APP_ENVIRONMENT`: Environment (development/production)

### Nginx Configuration

The deployment script creates an Nginx configuration with:
- ✅ Gzip compression
- ✅ Static asset caching
- ✅ SPA routing support
- ✅ API proxy to backend
- ✅ WebSocket proxy
- ✅ Security headers

### Docker Configuration

The Docker setup includes:
- ✅ Multi-stage build for optimization
- ✅ Nginx Alpine for minimal size
- ✅ Non-root user for security
- ✅ Health checks
- ✅ Proper caching headers

## 🔧 Backend Integration

### API Endpoints

The frontend expects these backend endpoints:

```
GET  /api/system/status     - System status
GET  /api/documents         - List documents
POST /api/documents/upload  - Upload document
POST /api/documents/search  - Search documents
POST /api/ai/analyze        - AI analysis
GET  /api/proxies           - List proxies
POST /api/proxies           - Add proxy
WS   /ws/                   - WebSocket connection
```

### CORS Configuration

Ensure your backend allows CORS from the frontend domain:

```python
# Flask example
from flask_cors import CORS

CORS(app, origins=[
    "http://localhost:3000",
    "https://your-domain.com"
])
```

## 📊 Performance Optimization

### Build Optimization
- ✅ Code splitting with manual chunks
- ✅ Tree shaking for unused code
- ✅ Gzip compression
- ✅ Asset optimization

### Runtime Optimization
- ✅ Lazy loading of components
- ✅ Image optimization
- ✅ Caching strategies
- ✅ Service worker (can be added)

## 🔒 Security

### Headers
- ✅ X-Frame-Options: SAMEORIGIN
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Content-Security-Policy

### Authentication
- JWT token storage in localStorage
- Automatic token refresh
- Secure API communication

## 📈 Monitoring

### Health Checks
- Frontend: `GET /health`
- Backend: `GET /api/system/health`

### Logging
- Application logs in `/var/log/iranian-legal-archive/`
- Nginx access logs
- Docker container logs

## 🚨 Troubleshooting

### Common Issues

1. **Build fails**: Check Node.js version (18+)
2. **API connection fails**: Verify backend is running
3. **WebSocket connection fails**: Check firewall/network
4. **Static assets not loading**: Check Nginx configuration

### Debug Commands

```bash
# Check build output
npm run build && ls -la dist/

# Test API connection
curl http://localhost:8000/api/system/status

# Check WebSocket
wscat -c ws://localhost:8000/ws

# View logs
docker-compose logs -f frontend
```

## 📞 Support

For issues or questions:
1. Check the logs first
2. Verify environment configuration
3. Test API connectivity
4. Review this deployment guide

---

**Built with ❤️ for the Iranian Legal Archive System**