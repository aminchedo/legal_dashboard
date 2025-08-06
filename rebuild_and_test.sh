#!/bin/bash

echo "🔧 Rebuilding and testing Legal Dashboard OCR Docker container..."

# Stop any running containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
docker stop legal-dashboard-ocr 2>/dev/null || true

# Remove old images
echo "Removing old images..."
docker rmi legal-dashboard-ocr 2>/dev/null || true

# Create data and cache directories
echo "Creating data and cache directories..."
mkdir -p data cache
chmod -R 777 data cache

# Build the new image
echo "Building new Docker image..."
docker build -t legal-dashboard-ocr .

# Test the container
echo "Testing container..."
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/cache:/app/cache legal-dashboard-ocr python debug_container.py

# Start with docker-compose
echo "Starting with docker-compose..."
docker-compose up --build -d

# Wait a moment for startup
echo "Waiting for application to start..."
sleep 10

# Test health endpoint
echo "Testing health endpoint..."
curl -f http://localhost:7860/health || echo "Health check failed"

echo "✅ Rebuild and test complete!"
echo "Access the application at: http://localhost:7860" 