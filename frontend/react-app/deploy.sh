#!/bin/bash

# Iranian Legal Archive System - Frontend Deployment Script
# This script builds and deploys the React frontend

set -e

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUILD_DIR="dist"
DEPLOY_DIR="/var/www/iranian-legal-archive"
BACKUP_DIR="/var/backups/iranian-legal-archive"
NGINX_CONFIG="/etc/nginx/sites-available/iranian-legal-archive"

echo -e "${BLUE}📦 Building React application...${NC}"
npm run build

if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}❌ Build directory not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed successfully${NC}"

# Create backup if deployment directory exists
if [ -d "$DEPLOY_DIR" ]; then
    echo -e "${YELLOW}📦 Creating backup of existing deployment...${NC}"
    sudo mkdir -p "$BACKUP_DIR"
    sudo cp -r "$DEPLOY_DIR" "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${GREEN}✅ Backup created${NC}"
fi

# Create deployment directory
echo -e "${BLUE}📁 Creating deployment directory...${NC}"
sudo mkdir -p "$DEPLOY_DIR"

# Copy build files
echo -e "${BLUE}📋 Copying build files...${NC}"
sudo cp -r "$BUILD_DIR"/* "$DEPLOY_DIR/"

# Set proper permissions
echo -e "${BLUE}🔐 Setting permissions...${NC}"
sudo chown -R www-data:www-data "$DEPLOY_DIR"
sudo chmod -R 755 "$DEPLOY_DIR"

# Create Nginx configuration
echo -e "${BLUE}⚙️ Creating Nginx configuration...${NC}"
sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;
    root $DEPLOY_DIR;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Handle client-side routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache static assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # API proxy (adjust port as needed)
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
echo -e "${BLUE}🔗 Enabling Nginx site...${NC}"
sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/

# Test Nginx configuration
echo -e "${BLUE}🧪 Testing Nginx configuration...${NC}"
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
    
    # Reload Nginx
    echo -e "${BLUE}🔄 Reloading Nginx...${NC}"
    sudo systemctl reload nginx
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}🌐 Application is available at: http://localhost${NC}"
    echo -e "${BLUE}📊 Build size: $(du -sh $BUILD_DIR | cut -f1)${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi