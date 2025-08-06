Write-Host "🔧 Rebuilding and testing Legal Dashboard OCR Docker container..." -ForegroundColor Green

# Stop any running containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
docker stop legal-dashboard-ocr 2>$null

# Remove old images
Write-Host "Removing old images..." -ForegroundColor Yellow
docker rmi legal-dashboard-ocr 2>$null

# Create data and cache directories
Write-Host "Creating data and cache directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "cache" | Out-Null

# Build the new image
Write-Host "Building new Docker image..." -ForegroundColor Yellow
docker build -t legal-dashboard-ocr .

# Test the container
Write-Host "Testing container..." -ForegroundColor Yellow
docker run --rm -v ${PWD}/data:/app/data -v ${PWD}/cache:/app/cache legal-dashboard-ocr python debug_container.py

# Start with docker-compose
Write-Host "Starting with docker-compose..." -ForegroundColor Yellow
docker-compose up --build -d

# Wait a moment for startup
Write-Host "Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:7860/health" -UseBasicParsing | Out-Null
    Write-Host "✅ Health check passed" -ForegroundColor Green
}
catch {
    Write-Host "❌ Health check failed" -ForegroundColor Red
}

Write-Host "✅ Rebuild and test complete!" -ForegroundColor Green
Write-Host "Access the application at: http://localhost:7860" -ForegroundColor Cyan 