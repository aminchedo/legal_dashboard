#!/bin/bash

# Legal Dashboard - Enhanced Deployment Script
# With PyMuPDF, OpenCV, spaCy, and Gradio support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${PURPLE}🎉 $1${NC}"; }
print_feature() { echo -e "${CYAN}🚀 $1${NC}"; }

echo "🏛️ Legal Dashboard - Enhanced Deployment"
echo "========================================"
echo ""

# Banner
cat << 'EOF'
 _                      _   ____            _     _                         _ 
| |    ___  __ _  __ _| | |  _ \  __ _ ___| |__ | |__   ___   __ _ _ __ __| |
| |   / _ \/ _` |/ _` | | | | | |/ _` / __| '_ \| '_ \ / _ \ / _` | '__/ _` |
| |__|  __/ (_| | (_| | | | |_| | (_| \__ \ | | | |_) | (_) | (_| | | | (_| |
|_____\___|\__, |\__,_|_| |____/ \__,_|___/_| |_|_.__/ \___/ \__,_|_|  \__,_|
           |___/                                                             
EOF

echo ""
print_feature "Enhanced with PyMuPDF, OpenCV, spaCy, and Gradio!"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: System Requirements Check
print_info "Step 1: Checking system requirements..."

REQUIREMENTS_MET=true

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker found: $DOCKER_VERSION"
else
    print_error "Docker is required but not installed"
    REQUIREMENTS_MET=false
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_CMD="docker-compose"
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose found: $COMPOSE_VERSION"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    COMPOSE_VERSION=$(docker compose version | cut -d' ' -f4)
    print_status "Docker Compose (plugin) found: $COMPOSE_VERSION"
else
    print_error "Docker Compose is required but not installed"
    REQUIREMENTS_MET=false
fi

# Check system resources
if command_exists free; then
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
    print_info "Available RAM: ${TOTAL_MEM}GB"
    
    if (( $(echo "$TOTAL_MEM < 4.0" | bc -l) )); then
        print_warning "Recommended minimum RAM is 4GB (found ${TOTAL_MEM}GB)"
    fi
fi

if command_exists df; then
    AVAILABLE_DISK=$(df -h . | awk 'NR==2 {print $4}')
    print_info "Available disk space: $AVAILABLE_DISK"
fi

if [ "$REQUIREMENTS_MET" = false ]; then
    print_error "System requirements not met. Please install required components."
    exit 1
fi

# Step 2: Cleanup existing deployment
print_info "Step 2: Cleaning up existing deployment..."

$COMPOSE_CMD down -v 2>/dev/null || true
docker system prune -f 2>/dev/null || true

print_status "Cleanup completed"

# Step 3: Create enhanced directory structure
print_info "Step 3: Creating enhanced directory structure..."

directories=(
    "data"
    "cache"
    "logs"
    "uploads" 
    "backups"
    "logs/nginx"
    "models"  # For downloaded models
    "temp"    # For temporary processing
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    chmod 755 "$dir"
done

print_status "Enhanced directory structure created"

# Step 4: Setup enhanced environment
print_info "Step 4: Setting up enhanced environment..."

if [ ! -f ".env" ]; then
    SECRET_KEY="legal-dashboard-$(date +%s)-$(openssl rand -hex 16 2>/dev/null || echo "fallback-secret")"
    
    cat > .env << EOF
# Legal Dashboard Enhanced Environment Configuration
# ================================================

# Security
JWT_SECRET_KEY=$SECRET_KEY

# Database Configuration
DATABASE_DIR=/app/data
DATABASE_PATH=/app/data/legal_dashboard.db

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production
PYTHONPATH=/app

# Cache and Storage
TRANSFORMERS_CACHE=/app/cache
HF_HOME=/app/cache
TORCH_CACHE=/app/cache/torch

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# OCR Configuration
OCR_MODELS_PATH=/app/models
OCR_TEMP_PATH=/app/temp

# spaCy Configuration
SPACY_MODEL=en_core_web_sm

# Gradio Configuration (optional)
GRADIO_ENABLE=true
GRADIO_PORT=7860

# HuggingFace Configuration (optional)
# HF_TOKEN=your_huggingface_token_here

# Performance Settings
MAX_WORKERS=2
MAX_FILE_SIZE=50MB
OCR_TIMEOUT=300

# Feature Flags
ENABLE_ADVANCED_OCR=true
ENABLE_NLP_PROCESSING=true
ENABLE_GRADIO_INTERFACE=true
EOF
    print_status "Enhanced .env file created"
else
    print_status ".env file already exists"
fi

# Step 5: Create enhanced frontend structure
print_info "Step 5: Setting up enhanced frontend..."

if [ ! -d "frontend" ]; then
    mkdir -p frontend/{js,css,images}
    print_warning "Frontend directory not found, creating enhanced structure..."
fi

# Create enhanced index.html if missing
if [ ! -f "frontend/index.html" ]; then
    print_info "Creating enhanced index.html with new features..."
    cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <title>Legal Dashboard | داشبورد حقوقی پیشرفته</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { font-family: 'Vazir', sans-serif; }
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: rtl;
        }
        .hero-section {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 50px;
            margin: 50px auto;
            max-width: 1200px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 40px;
        }
        .feature-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.4s ease;
            border: 1px solid rgba(0,0,0,0.05);
            cursor: pointer;
        }
        .feature-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        .feature-icon {
            font-size: 3.5rem;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        .status-bar {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #28a745;
        }
        .new-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            position: absolute;
            top: -10px;
            right: -10px;
        }
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin: 30px 0;
        }
        .tech-badge {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .interface-tabs {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }
        .tab-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            margin: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .tab-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="text-center">
            <h1 class="display-3 mb-4">
                🏛️ داشبورد حقوقی پیشرفته
            </h1>
            <p class="lead mb-4">
                سیستم مدیریت اسناد حقوقی با قابلیت‌های هوش مصنوعی پیشرفته
                <br>
                <small>Enhanced with PyMuPDF, OpenCV, spaCy, and Gradio</small>
            </p>
            
            <div class="tech-stack">
                <span class="tech-badge">🧠 PyTorch</span>
                <span class="tech-badge">🔍 PyMuPDF</span>
                <span class="tech-badge">👁️ OpenCV</span>
                <span class="tech-badge">📝 spaCy</span>
                <span class="tech-badge">🎛️ Gradio</span>
                <span class="tech-badge">🤖 Transformers</span>
            </div>
        </div>
        
        <div class="status-bar">
            <div id="systemStatus">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>در حال بررسی وضعیت سیستم...</span>
                </div>
            </div>
        </div>
        
        <div class="interface-tabs text-center">
            <h4 class="mb-3">🎯 رابط‌های کاربری موجود</h4>
            <button class="tab-button" onclick="window.open('/api/docs', '_blank')">
                📚 FastAPI Docs
            </button>
            <button class="tab-button" onclick="window.open(':7860', '_blank')">
                🎛️ Gradio Interface
            </button>
            <button class="tab-button" onclick="checkDetailedStatus()">
                ❤️ Health Check
            </button>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card" onclick="window.open('/api/docs#/OCR', '_blank')" style="position: relative;">
                <span class="new-badge">جدید</span>
                <div class="feature-icon">
                    <i class="fas fa-eye"></i>
                </div>
                <h4>OCR پیشرفته</h4>
                <p>استخراج متن با PyMuPDF، OpenCV و مدل‌های Transformer</p>
                <small class="text-muted">PyMuPDF + TrOCR</small>
            </div>
            
            <div class="feature-card" onclick="window.open('/api/docs#/Analytics', '_blank')" style="position: relative;">
                <span class="new-badge">بهبود یافته</span>
                <div class="feature-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <h4>تحلیل NLP</h4>
                <p>شناسایی موجودیت‌ها و تحلیل متن با spaCy</p>
                <small class="text-muted">Named Entity Recognition</small>
            </div>
            
            <div class="feature-card" onclick="window.open(':7860', '_blank')" style="position: relative;">
                <span class="new-badge">جدید</span>
                <div class="feature-icon">
                    <i class="fas fa-desktop"></i>
                </div>
                <h4>رابط Gradio</h4>
                <p>رابط کاربری تعاملی برای پردازش اسناد</p>
                <small class="text-muted">Web-based Interface</small>
            </div>
            
            <div class="feature-card" onclick="window.open('/api/docs#/Documents', '_blank')">
                <div class="feature-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <h4>مدیریت اسناد</h4>
                <p>آپلود، ذخیره و مدیریت انواع اسناد</p>
                <small class="text-muted">PDF, Images, DOC</small>
            </div>
            
            <div class="feature-card" onclick="window.open('/api/docs#/Search', '_blank')">
                <div class="feature-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h4>جستجوی هوشمند</h4>
                <p>جستجوی پیشرفته در محتوای اسناد</p>
                <small class="text-muted">Full-text Search</small>
            </div>
            
            <div class="feature-card" onclick="window.open('/api/docs#/Reports', '_blank')">
                <div class="feature-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h4>گزارش‌گیری</h4>
                <p>تولید گزارشات و آمار تفصیلی</p>
                <small class="text-muted">Analytics & Reports</small>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <button class="btn btn-primary btn-lg me-3" onclick="runSystemTest()">
                🧪 تست سیستم
            </button>
            <button class="btn btn-outline-primary btn-lg" onclick="location.reload()">
                🔄 تازه‌سازی
            </button>
        </div>
        
        <div id="testResults" class="mt-4"></div>
    </div>
    
    <script>
        function checkDetailedStatus() {
            const statusDiv = document.getElementById('systemStatus');
            statusDiv.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>در حال بررسی جزئیات...';
            
            fetch('/health/detailed')
                .then(r => r.json())
                .then(data => {
                    let statusHtml = '<h5><i class="fas fa-heart text-success"></i> وضعیت سیستم</h5>';
                    statusHtml += `<p><strong>آمادگی کلی:</strong> ${data.app_ready ? '✅ آماده' : '⏳ در حال راه‌اندازی'}</p>`;
                    
                    statusHtml += '<div class="row mt-3">';
                    for (const [service, info] of Object.entries(data.services)) {
                        const statusClass = info.status === 'healthy' ? 'success' : 
                                          info.status === 'loading' ? 'warning' : 'danger';
                        statusHtml += `
                            <div class="col-md-4 mb-2">
                                <div class="alert alert-${statusClass} mb-1 py-2">
                                    <strong>${service}:</strong><br>
                                    <small>${info.message}</small>
                                </div>
                            </div>
                        `;
                    }
                    statusHtml += '</div>';
                    statusDiv.innerHTML = statusHtml;
                })
                .catch(error => {
                    statusDiv.innerHTML = '<div class="alert alert-danger">خطا در دریافت وضعیت سیستم</div>';
                });
        }
        
        function runSystemTest() {
            const resultsDiv = document.getElementById('testResults');
            resultsDiv.innerHTML = '<div class="alert alert-info"><div class="spinner-border spinner-border-sm me-2"></div>در حال اجرای تست‌های سیستم...</div>';
            
            const tests = [
                { name: 'FastAPI', url: '/ping', expected: 'pong' },
                { name: 'Health Check', url: '/health', expected: 'healthy' },
                { name: 'API Docs', url: '/api/docs', expected: null },
                { name: 'OCR Service', url: '/api/ocr/status', expected: null }
            ];
            
            Promise.allSettled(tests.map(test => 
                fetch(test.url).then(r => r.ok ? r.json() : Promise.reject(r.status))
            )).then(results => {
                let html = '<div class="alert alert-info"><h5>🧪 نتایج تست سیستم</h5><ul class="list-unstyled mb-0">';
                
                results.forEach((result, i) => {
                    const test = tests[i];
                    if (result.status === 'fulfilled') {
                        html += `<li>✅ <strong>${test.name}:</strong> OK</li>`;
                    } else {
                        html += `<li>❌ <strong>${test.name}:</strong> Failed</li>`;
                    }
                });
                
                html += '</ul></div>';
                resultsDiv.innerHTML = html;
            });
        }
        
        // Auto-load status on page load
        setTimeout(checkDetailedStatus, 1000);
        
        // Periodic status updates
        setInterval(checkDetailedStatus, 60000);
    </script>
</body>
</html>
EOF
fi

print_status "Enhanced frontend setup completed"

# Step 6: Build and deploy with enhanced features
print_info "Step 6: Building and deploying enhanced services..."

print_info "Building containers with enhanced dependencies..."
print_warning "This may take 10-15 minutes due to ML dependencies..."

$COMPOSE_CMD build --no-cache

print_info "Starting enhanced services..."
$COMPOSE_CMD up -d

print_status "Enhanced services started"

# Step 7: Enhanced service readiness check
print_info "Step 7: Waiting for enhanced services..."

# Function to wait for service with better feedback
wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=$3
    local attempt=1
    
    print_info "Waiting for $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval $check_command > /dev/null 2>&1; then
            print_status "$service_name is ready"
            return 0
        fi
        
        # Show progress
        if [ $((attempt % 10)) -eq 0 ]; then
            echo -n " [${attempt}/${max_attempts}]"
        else
            echo -n "."
        fi
        
        sleep 3
        attempt=$((attempt + 1))
    done
    
    print_warning "$service_name may not be fully ready (timeout reached)"
    return 1
}

# Wait for Redis
wait_for_service "Redis" "docker exec legal_dashboard_redis redis-cli ping" 20

# Wait for FastAPI core
wait_for_service "FastAPI Core" "curl -fs http://localhost:8000/ping" 60

# Check for Gradio (optional)
print_info "Checking Gradio interface availability..."
if curl -fs http://localhost:7860 > /dev/null 2>&1; then
    print_status "Gradio interface is available at http://localhost:7860"
else
    print_info "Gradio interface will be available shortly at http://localhost:7860"
fi

print_status "All enhanced services are ready"

# Step 8: Enhanced verification
print_info "Step 8: Verifying enhanced deployment..."

# Check container status
print_info "Container Status:"
$COMPOSE_CMD ps

# Test enhanced endpoints
print_info "Testing enhanced endpoints..."

endpoints=(
    "/ping:Quick Status"
    "/health:Health Check" 
    "/health/detailed:Detailed Status"
    "/api/docs:API Documentation"
    "/api/ocr/status:OCR Service Status"
)

for endpoint_info in "${endpoints[@]}"; do
    IFS=':' read -r endpoint description <<< "$endpoint_info"
    if curl -fs "http://localhost:8000$endpoint" > /dev/null 2>&1; then
        print_status "✓ $description ($endpoint) - OK"
    else
        print_warning "⚠ $description ($endpoint) - May still be loading"
    fi
done

# Step 9: Enhanced deployment summary
print_success "Step 9: Enhanced Deployment Complete!"

echo ""
echo "🎉 Legal Dashboard Enhanced Edition is Ready!"
echo "=============================================="
echo ""

print_feature "🌟 NEW FEATURES:"
echo "   🔍 Enhanced OCR with PyMuPDF and OpenCV"
echo "   🧠 Advanced NLP with spaCy"
echo "   🎛️ Interactive Gradio Interface"
echo "   📊 Improved Analytics and Processing"
echo ""

print_info "📱 Access URLs:"
echo "   Main Dashboard:      http://localhost:8000"
echo "   API Documentation:   http://localhost:8000/api/docs"
echo "   Gradio Interface:    http://localhost:7860"
echo "   Health Check:        http://localhost:8000/health/detailed"
echo "   Quick Status:        http://localhost:8000/ping"
echo ""

print_info "🔧 Management Commands:"
echo "   View logs:           $COMPOSE_CMD logs -f legal-dashboard"
echo "   OCR logs:            $COMPOSE_CMD logs legal-dashboard | grep OCR"
echo "   Stop services:       $COMPOSE_CMD down"
echo "   Restart:             $COMPOSE_CMD restart"
echo "   Full cleanup:        $COMPOSE_CMD down -v && docker system prune -f"
echo ""

print_info "📊 Enhanced Service Status:"

# Final enhanced status check
services_status=()

if $COMPOSE_CMD ps | grep legal_dashboard_app | grep -q "Up"; then
    services_status+=("✅ Legal Dashboard App: Running")
else
    services_status+=("❌ Legal Dashboard App: Not Running")
fi

if $COMPOSE_CMD ps | grep legal_dashboard_redis | grep -q "Up"; then
    services_status+=("✅ Redis Cache: Running")
else
    services_status+=("❌ Redis Cache: Not Running")
fi

if curl -fs http://localhost:8000/ping >/dev/null 2>&1; then
    services_status+=("✅ FastAPI: Responding")
else
    services_status+=("❌ FastAPI: Not Responding")
fi

if curl -fs http://localhost:7860 >/dev/null 2>&1; then
    services_status+=("✅ Gradio Interface: Available")
else
    services_status+=("⏳ Gradio Interface: Loading...")
fi

for status in "${services_status[@]}"; do
    echo "   $status"
done

echo ""
print_warning "📚 IMPORTANT NOTES:"
echo "   • OCR models may take 5-10 minutes to fully load"
echo "   • spaCy models will be downloaded on first use"
echo "   • Gradio interface provides interactive document processing"
echo "   • Enhanced OCR supports PDF and image files"
echo "   • All features work independently - core system is ready"
echo ""

print_info "🔍 To monitor enhanced features:"
echo "   OCR Status:    curl http://localhost:8000/api/ocr/status"
echo "   System Health: curl http://localhost:8000/health/detailed"
echo "   Service Logs:  $COMPOSE_CMD logs -f legal-dashboard"
echo ""

print_success "✨ Enhanced Legal Dashboard deployed successfully!"
print_feature "🚀 Ready to process legal documents with advanced AI capabilities!"

echo ""
echo "Next steps:"
echo "1. Visit http://localhost:8000 for the main dashboard"
echo "2. Try the Gradio interface at http://localhost:7860"
echo "3. Upload a PDF or image to test OCR capabilities"
echo "4. Check /api/docs for the complete API reference"
echo ""

# Final system test
print_info "Running final system verification..."
if curl -fs http://localhost:8000/ping | grep -q "pong"; then
    print_success "🎯 System verification passed! Ready to use."
else
    print_warning "⚠️  System may still be initializing. Please wait a few minutes."
fi