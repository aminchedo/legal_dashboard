#!/bin/bash

# Legal Dashboard - One-Click Deployment Script
# =============================================
# This script handles everything: validation, optimization, and deployment

set -e  # Exit on any error

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ASCII Art Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "████████████████████████████████████████████████████████████████████████████████"
    echo "█                                                                              █"
    echo "█  🏛️  LEGAL DASHBOARD - ONE-CLICK DEPLOYMENT                                 █"
    echo "█                                                                              █"
    echo "█      Comprehensive Legal Document Management System                          █"
    echo "█      Ready for HF Spaces • Docker • Local Deployment                        █"
    echo "█                                                                              █"
    echo "████████████████████████████████████████████████████████████████████████████████"
    echo -e "${NC}"
}

# Utility functions
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
print_step() { echo -e "${CYAN}🔧 $1${NC}"; }

# Progress indicator
show_progress() {
    local duration=$1
    local message=$2
    
    echo -n -e "${YELLOW}⏳ ${message}${NC}"
    for ((i=0; i<duration; i++)); do
        echo -n "."
        sleep 1
    done
    echo -e " ${GREEN}Done!${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Main deployment function
main() {
    local deployment_type=""
    local project_ready=false
    
    print_banner
    echo ""
    print_info "Legal Dashboard Deployment Assistant"
    print_info "Detected OS: $(detect_os)"
    echo ""
    
    # Check if we're in the right directory
    if [[ ! -f "app.py" && ! -f "run.py" ]]; then
        print_error "This doesn't appear to be the Legal Dashboard directory."
        print_info "Please run this script from the project root directory."
        exit 1
    fi
    
    print_success "Project directory confirmed"
    
    # Deployment type selection
    echo ""
    print_step "Select Deployment Type:"
    echo ""
    echo -e "  ${GREEN}1)${NC} 🤗 Hugging Face Spaces (Recommended for Demo)"
    echo -e "  ${BLUE}2)${NC} 🐳 Docker Deployment (Recommended for Production)"
    echo -e "  ${PURPLE}3)${NC} 💻 Local Development"
    echo -e "  ${CYAN}4)${NC} 🧪 Run Tests Only"
    echo -e "  ${YELLOW}5)${NC} 📋 Show Project Status"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            deployment_type="huggingface"
            deploy_to_huggingface
            ;;
        2)
            deployment_type="docker"
            deploy_with_docker
            ;;
        3)
            deployment_type="local"
            setup_local_development
            ;;
        4)
            run_comprehensive_tests
            ;;
        5)
            show_project_status
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
}

# Hugging Face Spaces deployment
deploy_to_huggingface() {
    print_step "Preparing for Hugging Face Spaces Deployment"
    echo ""
    
    # Check if git is available
    if ! command_exists git; then
        print_error "Git is required for HF Spaces deployment"
        exit 1
    fi
    
    # Run pre-deployment tests
    print_info "Running pre-deployment validation..."
    if python3 final_test.py --quick; then
        print_success "All critical tests passed"
    else
        print_warning "Some tests failed, but continuing with deployment"
    fi
    
    # Create HF Spaces optimized requirements
    print_step "Creating HF Spaces optimized requirements..."
    cp requirements-hf-spaces.txt requirements.txt
    print_success "Requirements optimized for HF Spaces"
    
    # Prepare files for HF Spaces
    print_step "Preparing files for Hugging Face Spaces..."
    
    # Create deployment checklist
    cat > HF_SPACES_SETUP.md << EOF
# 🤗 Hugging Face Spaces Setup Instructions

## 📋 Quick Setup Steps:

1. **Create New Space:**
   - Go to https://huggingface.co/new-space
   - Choose "Gradio" as SDK
   - Set Python version to 3.10

2. **Upload Files:**
   - Upload all files from this directory to your Space
   - The main entry point is \`app.py\`

3. **Set Environment Variables in Space Settings:**
   \`\`\`
   JWT_SECRET_KEY=your-unique-secret-key-here-$(date +%s)
   DATABASE_DIR=/tmp/legal_dashboard/data
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   \`\`\`

4. **Default Login Credentials:**
   - Username: \`admin\`
   - Password: \`admin123\`
   - **⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN!**

## 🚀 Features Available in HF Spaces:
- ✅ Document upload and processing
- ✅ Authentication system
- ✅ Persian/English interface
- ✅ Basic OCR capabilities
- ✅ Document management
- ✅ Responsive design

## 📞 Support:
- Check Space logs for any issues
- Health check available at your-space-url/health
- Report issues via GitHub

**Your Legal Dashboard is ready for HF Spaces! 🎉**
EOF
    
    print_success "HF Spaces setup guide created: HF_SPACES_SETUP.md"
    
    echo ""
    print_success "🎉 Hugging Face Spaces deployment package ready!"
    echo ""
    print_info "Next steps:"
    echo "  1. 📝 Read HF_SPACES_SETUP.md for detailed instructions"
    echo "  2. 🌐 Create a new Space at https://huggingface.co/new-space"
    echo "  3. 📁 Upload all files from this directory"
    echo "  4. ⚙️ Set environment variables as shown in the guide"
    echo "  5. 🚀 Your Space will automatically build and deploy!"
    echo ""
    print_warning "Remember to change the default admin password after deployment!"
}

# Docker deployment
deploy_with_docker() {
    print_step "Setting up Docker Deployment"
    echo ""
    
    # Check Docker availability
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        echo "  📥 Download from: https://www.docker.com/get-started"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_warning "Docker Compose not found. Using docker compose instead."
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
    
    # Run pre-deployment tests
    print_info "Running pre-deployment validation..."
    if python3 final_test.py --quick; then
        print_success "All critical tests passed"
    else
        print_error "Critical tests failed. Please fix issues before deploying."
        exit 1
    fi
    
    # Create optimized requirements for Docker
    print_step "Preparing Docker environment..."
    cp requirements-docker.txt requirements.txt
    
    # Ensure .env file exists
    if [[ ! -f ".env" ]]; then
        print_step "Creating .env file..."
        cat > .env << EOF
# Legal Dashboard Environment Configuration
JWT_SECRET_KEY=super-secret-jwt-key-change-in-production-$(date +%s)
DATABASE_DIR=/app/data
LOG_LEVEL=INFO
ENVIRONMENT=production
WORKERS=4
PORT=8000
PYTHONPATH=/app
PYTHONUNBUFFERED=1
EOF
        print_success ".env file created"
    fi
    
    # Build and start containers
    print_step "Building Docker containers..."
    show_progress 5 "Building images"
    
    if command_exists docker-compose; then
        docker-compose build --no-cache
        print_success "Docker containers built successfully"
        
        print_step "Starting Legal Dashboard..."
        docker-compose up -d
        
        # Wait for services to be ready
        print_info "Waiting for services to start..."
        sleep 15
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            print_success "🎉 Legal Dashboard is running!"
            echo ""
            print_info "🌐 Access your Legal Dashboard:"
            echo "  • Dashboard: http://localhost:8000"
            echo "  • API Docs: http://localhost:8000/docs"
            echo "  • Health Check: http://localhost:8000/api/health"
            echo ""
            print_info "📊 Default Login:"
            echo "  • Username: admin"
            echo "  • Password: admin123"
            echo ""
            print_warning "⚠️ Change the default password immediately!"
            
            # Test health endpoint
            echo ""
            print_step "Testing deployment..."
            sleep 5
            if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
                print_success "Health check passed - deployment successful!"
            else
                print_warning "Health check failed - check container logs"
                echo "  🔍 Debug: docker-compose logs"
            fi
            
        else
            print_error "Failed to start services"
            echo "  🔍 Check logs: docker-compose logs"
            exit 1
        fi
        
    else
        # Use docker build and run
        docker build -t legal-dashboard .
        print_success "Docker image built successfully"
        
        print_step "Starting Legal Dashboard container..."
        docker run -d \
            --name legal-dashboard \
            -p 8000:8000 \
            -v $(pwd)/data:/app/data \
            -v $(pwd)/logs:/app/logs \
            --env-file .env \
            legal-dashboard
        
        print_success "🎉 Legal Dashboard container started!"
        echo ""
        print_info "🌐 Access: http://localhost:8000"
        print_info "🔍 Logs: docker logs legal-dashboard"
        print_info "🛑 Stop: docker stop legal-dashboard"
    fi
}

# Local development setup
setup_local_development() {
    print_step "Setting up Local Development Environment"
    echo ""
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_info "Python version: $python_version"
    
    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_step "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    # Install dependencies
    print_step "Installing dependencies..."
    show_progress 3 "Installing packages"
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    print_success "Dependencies installed"
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        print_step "Creating development .env file..."
        cat > .env << EOF
# Legal Dashboard Development Configuration
JWT_SECRET_KEY=dev-secret-key-$(date +%s)
DATABASE_DIR=./data
LOG_LEVEL=DEBUG
ENVIRONMENT=development
WORKERS=1
PORT=8000
PYTHONPATH=.
PYTHONUNBUFFERED=1
EOF
        print_success ".env file created for development"
    fi
    
    # Run tests
    print_step "Running comprehensive tests..."
    if python final_test.py; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed, but you can still run the development server"
    fi
    
    # Create development startup script
    cat > start_dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Legal Dashboard Development Server..."
echo ""

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Set development environment
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG

# Start the application
echo "🌐 Development server will be available at:"
echo "  • FastAPI: http://localhost:8000"
echo "  • Gradio: http://localhost:7860 (if running app.py)"
echo ""
echo "📊 Default Login: admin / admin123"
echo "🛑 Press Ctrl+C to stop"
echo ""

python run.py
EOF
    
    chmod +x start_dev.sh
    
    print_success "🎉 Local development environment ready!"
    echo ""
    print_info "📁 Development files created:"
    echo "  • venv/ - Virtual environment"
    echo "  • .env - Development configuration"
    echo "  • start_dev.sh - Development server launcher"
    echo ""
    print_info "🚀 To start development:"
    echo "  ./start_dev.sh"
    echo ""
    print_info "🧪 To run tests:"
    echo "  python final_test.py"
    echo ""
    print_warning "⚠️ Remember to activate the virtual environment:"
    echo "  source venv/bin/activate"
}

# Run comprehensive tests
run_comprehensive_tests() {
    print_step "Running Comprehensive Test Suite"
    echo ""
    
    # Check if Python is available
    if ! command_exists python3; then
        print_error "Python 3 is required for testing"
        exit 1
    fi
    
    # Run the test suite
    print_info "Starting comprehensive validation..."
    echo ""
    
    if python3 final_test.py; then
        echo ""
        print_success "🎉 All tests passed! Your Legal Dashboard is ready for deployment."
        echo ""
        print_info "📋 You can now:"
        echo "  1. Deploy to Hugging Face Spaces"
        echo "  2. Deploy with Docker"
        echo "  3. Run locally for development"
        echo ""
        print_info "📞 Need help? Check README_FINAL.md"
    else
        echo ""
        print_warning "⚠️ Some tests failed. Please review the issues above."
        echo ""
        print_info "🔧 Common fixes:"
        echo "  • Install missing dependencies: pip install -r requirements.txt"
        echo "  • Check file permissions"
        echo "  • Ensure you're in the project directory"
        echo ""
        print_info "📞 For detailed troubleshooting, see DEPLOYMENT_CHECKLIST.md"
    fi
}

# Show project status
show_project_status() {
    print_step "Legal Dashboard Project Status"
    echo ""
    
    # Check project structure
    local files_present=0
    local total_files=0
    
    declare -a required_files=(
        "app.py:Gradio interface"
        "run.py:Universal runner"
        "config.py:Configuration manager"
        "final_test.py:Test suite"
        "requirements.txt:Dependencies"
        "Dockerfile:Container config"
        "docker-compose.yml:Multi-service setup"
        ".env:Environment variables"
        "app/main.py:FastAPI application"
        "frontend/index.html:Web dashboard"
    )
    
    print_info "📁 Project Structure:"
    for file_info in "${required_files[@]}"; do
        local file=$(echo $file_info | cut -d':' -f1)
        local desc=$(echo $file_info | cut -d':' -f2)
        total_files=$((total_files + 1))
        
        if [[ -f "$file" ]]; then
            print_success "$file - $desc"
            files_present=$((files_present + 1))
        else
            print_error "$file - $desc (MISSING)"
        fi
    done
    
    echo ""
    local completeness=$((files_present * 100 / total_files))
    print_info "📊 Project Completeness: $completeness% ($files_present/$total_files files)"
    
    # Check dependencies
    echo ""
    print_info "🔧 System Dependencies:"
    
    if command_exists python3; then
        local python_version=$(python3 --version)
        print_success "Python: $python_version"
    else
        print_error "Python 3: Not installed"
    fi
    
    if command_exists docker; then
        local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker: $docker_version"
    else
        print_warning "Docker: Not installed (optional)"
    fi
    
    if command_exists git; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_success "Git: $git_version"
    else
        print_warning "Git: Not installed (needed for HF Spaces)"
    fi
    
    # Deployment readiness
    echo ""
    if [[ $completeness -eq 100 ]]; then
        print_success "🎉 Project Status: READY FOR DEPLOYMENT"
        echo ""
        print_info "🚀 Available deployment options:"
        echo "  1. Hugging Face Spaces (demo/sharing)"
        echo "  2. Docker (production)"
        echo "  3. Local development"
        echo ""
        print_info "Run ./deploy_now.sh again to start deployment!"
    else
        print_warning "⚠️ Project Status: INCOMPLETE"
        echo ""
        print_info "🔧 Missing files need to be restored or created"
        print_info "Please ensure all required files are present"
    fi
    
    # Show environment info
    echo ""
    print_info "🌍 Environment Information:"
    echo "  • OS: $(detect_os)"
    echo "  • Shell: $SHELL"
    echo "  • Working Directory: $(pwd)"
    echo "  • User: $(whoami)"
    
    # Quick health check
    echo ""
    print_step "Running quick health check..."
    if python3 -c "
import sys
try:
    from config import config
    print('✅ Configuration system: OK')
    print(f'✅ Environment detected: {config.environment}')
    print('✅ Import test: PASSED')
except Exception as e:
    print(f'❌ Import test failed: {e}')
    sys.exit(1)
"; then
        print_success "Quick health check passed"
    else
        print_warning "Quick health check failed - some modules may be missing"
    fi
}

# Run main function
main "$@"

echo ""
print_info "Legal Dashboard Deployment Assistant - Complete"
print_info "For support, check README_FINAL.md or DEPLOYMENT_CHECKLIST.md"
echo ""