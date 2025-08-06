# Legal Dashboard OCR - Test Suite

This directory contains all test files for the Legal Dashboard OCR project, organized by category for better maintainability and discovery.

## 📁 Directory Structure

```
tests/
├── backend/           # Backend API and service tests
│   ├── test_api_endpoints.py
│   ├── test_ocr_pipeline.py
│   ├── test_ocr_fixes.py
│   ├── test_hf_deployment_fixes.py
│   ├── test_db_connection.py
│   ├── test_structure.py
│   ├── validate_fixes.py
│   └── verify_frontend.py
│
└── docker/            # Docker and deployment tests
    ├── test_docker.py
    ├── validate_docker_setup.py
    ├── simple_validation.py
    ├── test_hf_deployment.py
    └── deployment_validation.py
```

## 🧪 Test Categories

### Backend Tests (`tests/backend/`)

**API Endpoint Tests:**
- `test_api_endpoints.py` - Tests all FastAPI endpoints
- `test_ocr_pipeline.py` - Tests OCR pipeline functionality
- `test_db_connection.py` - Tests database connectivity

**Fix Validation Tests:**
- `test_ocr_fixes.py` - Validates OCR pipeline fixes
- `test_hf_deployment_fixes.py` - Validates Hugging Face deployment fixes
- `validate_fixes.py` - Comprehensive fix validation

**Structure and Frontend Tests:**
- `test_structure.py` - Tests project structure integrity
- `verify_frontend.py` - Tests frontend integration

### Docker Tests (`tests/docker/`)

**Docker Setup Tests:**
- `test_docker.py` - Tests Docker container functionality
- `validate_docker_setup.py` - Validates Docker configuration
- `simple_validation.py` - Basic Docker validation

**Deployment Tests:**
- `test_hf_deployment.py` - Tests Hugging Face deployment
- `deployment_validation.py` - Comprehensive deployment validation

## 🚀 Running Tests

### Method 1: Using the Test Runner

```bash
# Run all tests
python run_tests.py

# Run only backend tests
python run_tests.py --backend

# Run only docker tests
python run_tests.py --docker

# Run with pytest
python run_tests.py --pytest
```

### Method 2: Using pytest directly

```bash
# Run all tests
pytest tests/

# Run backend tests only
pytest tests/backend/

# Run docker tests only
pytest tests/docker/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/backend/test_api_endpoints.py
```

### Method 3: Running Individual Tests

```bash
# Backend tests
python tests/backend/test_api_endpoints.py
python tests/backend/test_ocr_pipeline.py
python tests/backend/test_ocr_fixes.py

# Docker tests
python tests/docker/test_docker.py
python tests/docker/validate_docker_setup.py
```

## 📋 Test Configuration

### pytest.ini
The project includes a `pytest.ini` file that configures:
- Test discovery paths
- Python file patterns
- Test class and function patterns
- Output formatting

### Test Runner Script
The `run_tests.py` script provides:
- Categorized test execution
- Detailed output formatting
- Error handling and reporting
- Support for different test types

## 🔧 Test Dependencies

All tests require the following dependencies (already in `requirements.txt`):
- `pytest==7.4.3`
- `pytest-asyncio==0.21.1`
- `fastapi`
- `transformers`
- `torch`
- Other project dependencies

## 📊 Test Coverage

### Backend Coverage
- ✅ API endpoint functionality
- ✅ OCR pipeline operations
- ✅ Database operations
- ✅ Error handling
- ✅ Fix validation

### Docker Coverage
- ✅ Container build process
- ✅ Environment setup
- ✅ Service initialization
- ✅ Deployment validation

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd legal_dashboard_ocr
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Connection Issues**
   ```bash
   # Ensure database directory exists
   mkdir -p /tmp/data
   ```

4. **Docker Issues**
   ```bash
   # Ensure Docker is running
   docker --version
   docker-compose --version
   ```

### Debug Mode

Run tests with debug output:
```bash
python run_tests.py --pytest -v
```

## 📈 Adding New Tests

### Backend Tests
1. Create test file in `tests/backend/`
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures and assertions
4. Add to test runner if needed

### Docker Tests
1. Create test file in `tests/docker/`
2. Test Docker-specific functionality
3. Validate deployment configurations
4. Ensure proper cleanup

### Test Guidelines
- Use descriptive test names
- Include setup and teardown
- Handle errors gracefully
- Provide clear failure messages
- Clean up resources after tests

## 🔄 Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Backend Tests
  run: python run_tests.py --backend

- name: Run Docker Tests
  run: python run_tests.py --docker

- name: Run All Tests
  run: python run_tests.py --pytest
```

## 📝 Test Documentation

Each test file includes:
- Purpose and scope
- Dependencies and setup
- Expected outcomes
- Error scenarios
- Cleanup procedures

## 🎯 Success Criteria

Tests are considered successful when:
- ✅ All test files execute without errors
- ✅ API endpoints respond correctly
- ✅ OCR pipeline processes documents
- ✅ Database operations complete
- ✅ Docker containers build and run
- ✅ Deployment configurations validate
- ✅ Error handling works as expected

---

**Last Updated:** Project reorganization completed  
**Test Coverage:** Comprehensive backend and docker testing  
**Status:** ✅ Ready for production deployment 