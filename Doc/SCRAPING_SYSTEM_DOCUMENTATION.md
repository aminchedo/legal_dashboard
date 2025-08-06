# Legal Dashboard - Scraping & Rating System Documentation

## Overview

The Legal Dashboard Scraping & Rating System is a comprehensive web scraping and data quality evaluation platform designed specifically for legal document processing. The system provides advanced scraping capabilities with multiple strategies, intelligent data rating, and a modern web dashboard for monitoring and control.

## Features

### 🕷️ Advanced Web Scraping
- **Multiple Scraping Strategies**: General, Legal Documents, News Articles, Academic Papers, Government Sites, Custom
- **Async Processing**: High-performance asynchronous scraping with configurable delays
- **Content Extraction**: Intelligent content extraction based on strategy and page structure
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in rate limiting to respect website policies

### ⭐ Intelligent Data Rating
- **Multi-Criteria Evaluation**: Source credibility, content completeness, OCR accuracy, data freshness, content relevance, technical quality
- **Dynamic Scoring**: Real-time rating updates as data is processed
- **Quality Indicators**: Automatic detection of legal document patterns and quality markers
- **Confidence Scoring**: Statistical confidence levels for rating accuracy

### 📊 Real-Time Dashboard
- **Live Monitoring**: Real-time job progress and system statistics
- **Interactive Charts**: Rating distribution and language analysis
- **Job Management**: Start, monitor, and control scraping jobs
- **Data Visualization**: Comprehensive statistics and analytics

### 🔧 API-First Design
- **RESTful API**: Complete REST API for all operations
- **WebSocket Support**: Real-time updates and notifications
- **Comprehensive Endpoints**: Full CRUD operations for scraping and rating
- **Health Monitoring**: System health checks and status monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   Dashboard     │◄──►│   Backend       │◄──►│   SQLite        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Services      │
                       │                 │
                       │ • Scraping      │
                       │ • Rating        │
                       │ • OCR           │
                       └─────────────────┘
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- FastAPI
- SQLite3
- Required Python packages (see requirements.txt)

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd legal_dashboard_ocr
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the application**:
```bash
cd legal_dashboard_ocr
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Access the dashboard**:
```
http://localhost:8000/scraping_dashboard.html
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t legal-dashboard-scraping .

# Run the container
docker run -p 8000:8000 legal-dashboard-scraping
```

## API Reference

### Scraping Endpoints

#### POST /api/scrape
Start a new scraping job.

**Request Body**:
```json
{
  "urls": ["https://example.com/page1", "https://example.com/page2"],
  "strategy": "legal_documents",
  "keywords": ["contract", "agreement"],
  "content_types": ["html", "pdf"],
  "max_depth": 1,
  "delay_between_requests": 1.0
}
```

**Response**:
```json
{
  "job_id": "scrape_job_20240101_120000_abc123",
  "status": "started",
  "message": "Scraping job started successfully with 2 URLs"
}
```

#### GET /api/scrape/status
Get status of all scraping jobs.

**Response**:
```json
[
  {
    "job_id": "scrape_job_20240101_120000_abc123",
    "status": "processing",
    "total_items": 2,
    "completed_items": 1,
    "failed_items": 0,
    "progress": 0.5,
    "created_at": "2024-01-01T12:00:00Z",
    "strategy": "legal_documents"
  }
]
```

#### GET /api/scrape/items
Get scraped items with optional filtering.

**Query Parameters**:
- `job_id` (optional): Filter by job ID
- `limit` (default: 100): Maximum items to return
- `offset` (default: 0): Number of items to skip

**Response**:
```json
[
  {
    "id": "item_20240101_120000_def456",
    "url": "https://example.com/page1",
    "title": "Legal Document Title",
    "content": "Extracted content...",
    "metadata": {...},
    "timestamp": "2024-01-01T12:00:00Z",
    "rating_score": 0.85,
    "processing_status": "completed",
    "word_count": 1500,
    "language": "english",
    "domain": "example.com"
  }
]
```

### Rating Endpoints

#### POST /api/rating/rate-all
Rate all unrated scraped items.

**Response**:
```json
{
  "total_items": 50,
  "rated_count": 45,
  "failed_count": 5,
  "message": "Rated 45 items, 5 failed"
}
```

#### GET /api/rating/summary
Get comprehensive rating summary.

**Response**:
```json
{
  "total_rated": 100,
  "average_score": 0.75,
  "score_range": {
    "min": 0.2,
    "max": 0.95
  },
  "average_confidence": 0.82,
  "rating_level_distribution": {
    "excellent": 25,
    "good": 40,
    "average": 25,
    "poor": 10
  },
  "criteria_averages": {
    "source_credibility": 0.8,
    "content_completeness": 0.7,
    "ocr_accuracy": 0.85
  },
  "recent_ratings_24h": 15
}
```

#### GET /api/rating/low-quality
Get items with low quality ratings.

**Query Parameters**:
- `threshold` (default: 0.4): Quality threshold
- `limit` (default: 50): Maximum items to return

**Response**:
```json
{
  "threshold": 0.4,
  "total_items": 10,
  "items": [...]
}
```

## Scraping Strategies

### 1. General Strategy
- Extracts all text content from web pages
- Suitable for general web scraping tasks
- Minimal content filtering

### 2. Legal Documents Strategy
- Focuses on legal document content
- Extracts structured legal text
- Identifies legal patterns and terminology
- Optimized for Persian and English legal content

### 3. News Articles Strategy
- Extracts news article content
- Removes navigation and advertising
- Focuses on article body and headlines

### 4. Academic Papers Strategy
- Extracts academic content
- Preserves citations and references
- Maintains document structure

### 5. Government Sites Strategy
- Optimized for government websites
- Extracts official documents and announcements
- Handles government-specific content structures

### 6. Custom Strategy
- User-defined content extraction rules
- Configurable selectors and patterns
- Flexible content processing

## Rating Criteria

### Source Credibility (25%)
- Domain authority and reputation
- Government/educational institution status
- HTTPS security
- Official indicators in metadata

### Content Completeness (25%)
- Word count and content length
- Structured content (chapters, sections)
- Legal document patterns
- Quality indicators

### OCR Accuracy (20%)
- Text quality and readability
- Character recognition accuracy
- Sentence structure quality
- Formatting consistency

### Data Freshness (15%)
- Content age and timeliness
- Update frequency
- Historical relevance

### Content Relevance (10%)
- Legal terminology density
- Domain-specific language
- Official language indicators

### Technical Quality (5%)
- Document structure
- Formatting consistency
- Metadata quality
- Content organization

## Database Schema

### scraped_items Table
```sql
CREATE TABLE scraped_items (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    metadata TEXT,
    timestamp TEXT,
    source_url TEXT,
    rating_score REAL DEFAULT 0.0,
    processing_status TEXT DEFAULT 'pending',
    error_message TEXT,
    strategy_used TEXT,
    content_hash TEXT,
    word_count INTEGER DEFAULT 0,
    language TEXT DEFAULT 'unknown',
    domain TEXT
);
```

### rating_results Table
```sql
CREATE TABLE rating_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    overall_score REAL,
    criteria_scores TEXT,
    rating_level TEXT,
    confidence REAL,
    timestamp TEXT,
    evaluator TEXT,
    notes TEXT,
    FOREIGN KEY (item_id) REFERENCES scraped_items (id)
);
```

### scraping_jobs Table
```sql
CREATE TABLE scraping_jobs (
    job_id TEXT PRIMARY KEY,
    urls TEXT,
    strategy TEXT,
    keywords TEXT,
    content_types TEXT,
    max_depth INTEGER DEFAULT 1,
    delay_between_requests REAL DEFAULT 1.0,
    timeout INTEGER DEFAULT 30,
    created_at TEXT,
    status TEXT DEFAULT 'pending',
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0
);
```

## Configuration

### Rating Configuration
```python
from app.services.rating_service import RatingConfig

config = RatingConfig(
    source_credibility_weight=0.25,
    content_completeness_weight=0.25,
    ocr_accuracy_weight=0.20,
    data_freshness_weight=0.15,
    content_relevance_weight=0.10,
    technical_quality_weight=0.05,
    excellent_threshold=0.8,
    good_threshold=0.6,
    average_threshold=0.4,
    poor_threshold=0.2
)
```

### Scraping Configuration
```python
from app.services.scraping_service import ScrapingService

scraping_service = ScrapingService(
    db_path="legal_documents.db",
    max_workers=10,
    timeout=30,
    user_agent="Legal-Dashboard-Scraper/1.0"
)
```

## Usage Examples

### Starting a Scraping Job
```python
import asyncio
from app.services.scraping_service import ScrapingService, ScrapingStrategy

async def scrape_legal_documents():
    service = ScrapingService()
    
    urls = [
        "https://court.gov.ir/document1",
        "https://justice.gov.ir/document2"
    ]
    
    job_id = await service.start_scraping_job(
        urls=urls,
        strategy=ScrapingStrategy.LEGAL_DOCUMENTS,
        keywords=["قرارداد", "contract", "agreement"],
        max_depth=1,
        delay=2.0
    )
    
    print(f"Started scraping job: {job_id}")

# Run the scraping job
asyncio.run(scrape_legal_documents())
```

### Rating Scraped Items
```python
import asyncio
from app.services.rating_service import RatingService

async def rate_items():
    service = RatingService()
    
    # Get scraped items
    items = await scraping_service.get_scraped_items()
    
    # Rate each item
    for item in items:
        if item['rating_score'] == 0.0:  # Unrated items
            result = await service.rate_item(item)
            print(f"Rated item {item['id']}: {result.rating_level.value} ({result.overall_score})")

# Run the rating process
asyncio.run(rate_items())
```

### API Integration
```python
import requests

# Start a scraping job
response = requests.post("http://localhost:8000/api/scrape", json={
    "urls": ["https://example.com/legal-doc"],
    "strategy": "legal_documents",
    "max_depth": 1
})

job_id = response.json()["job_id"]

# Monitor job progress
while True:
    status_response = requests.get(f"http://localhost:8000/api/scrape/status/{job_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        break
    
    time.sleep(5)

# Get rated items
items_response = requests.get("http://localhost:8000/api/scrape/items")
items = items_response.json()

# Get rating summary
summary_response = requests.get("http://localhost:8000/api/rating/summary")
summary = summary_response.json()
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/test_scraping_system.py -v

# Run specific test categories
pytest tests/test_scraping_system.py::TestScrapingService -v
pytest tests/test_scraping_system.py::TestRatingService -v
pytest tests/test_scraping_system.py::TestScrapingAPI -v

# Run with coverage
pytest tests/test_scraping_system.py --cov=app.services --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: REST API endpoint testing
- **Performance Tests**: Load and stress testing
- **Error Handling Tests**: Exception and error scenario testing

## Monitoring & Logging

### Log Levels
- **INFO**: General operational information
- **WARNING**: Non-critical issues and warnings
- **ERROR**: Error conditions and failures
- **DEBUG**: Detailed debugging information

### Key Metrics
- **Scraping Jobs**: Active jobs, completion rates, failure rates
- **Data Quality**: Average ratings, rating distributions, quality trends
- **System Performance**: Response times, throughput, resource usage
- **Error Rates**: Failed requests, parsing errors, rating failures

### Health Checks
```bash
# Check system health
curl http://localhost:8000/api/health

# Check scraping service health
curl http://localhost:8000/api/scrape/statistics

# Check rating service health
curl http://localhost:8000/api/rating/summary
```

## Troubleshooting

### Common Issues

#### 1. Scraping Jobs Not Starting
**Symptoms**: Jobs remain in "pending" status
**Solutions**:
- Check network connectivity
- Verify URL accessibility
- Review rate limiting settings
- Check server logs for errors

#### 2. Low Rating Scores
**Symptoms**: Items consistently getting low ratings
**Solutions**:
- Review content quality and completeness
- Check source credibility settings
- Adjust rating criteria weights
- Verify OCR accuracy for text extraction

#### 3. Database Errors
**Symptoms**: Database connection failures or data corruption
**Solutions**:
- Check database file permissions
- Verify SQLite installation
- Review database schema
- Check for disk space issues

#### 4. Performance Issues
**Symptoms**: Slow response times or high resource usage
**Solutions**:
- Reduce concurrent scraping jobs
- Increase delay between requests
- Optimize database queries
- Review memory usage patterns

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Error Recovery
The system includes automatic error recovery mechanisms:
- **Job Retry**: Failed scraping jobs can be retried
- **Data Validation**: Automatic validation of scraped content
- **Graceful Degradation**: System continues operating with partial failures
- **Error Logging**: Comprehensive error logging for analysis

## Security Considerations

### Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Access Control**: API authentication and authorization
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Protection against abuse

### Privacy Compliance
- **Data Retention**: Configurable data retention policies
- **User Consent**: Respect for website terms of service
- **Data Minimization**: Only necessary data is collected
- **Right to Deletion**: User data can be deleted on request

### Network Security
- **HTTPS**: All communications encrypted
- **Certificate Validation**: Proper SSL certificate validation
- **Firewall Rules**: Network access controls
- **DDoS Protection**: Rate limiting and traffic filtering

## Performance Optimization

### Scraping Performance
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: Cache frequently accessed content
- **Parallel Processing**: Multiple concurrent scraping jobs

### Database Performance
- **Indexing**: Optimized database indexes
- **Query Optimization**: Efficient SQL queries
- **Connection Pooling**: Database connection management
- **Data Archiving**: Automatic archiving of old data

### Memory Management
- **Streaming**: Process large datasets in chunks
- **Garbage Collection**: Proper memory cleanup
- **Resource Limits**: Configurable memory limits
- **Monitoring**: Real-time memory usage tracking

## Future Enhancements

### Planned Features
- **Machine Learning**: Advanced content classification
- **Natural Language Processing**: Enhanced text analysis
- **Multi-language Support**: Additional language support
- **Cloud Integration**: Cloud storage and processing
- **Advanced Analytics**: Detailed analytics and reporting

### Scalability Improvements
- **Microservices Architecture**: Service decomposition
- **Load Balancing**: Distributed processing
- **Caching Layer**: Redis integration
- **Message Queues**: Asynchronous processing

## Support & Contributing

### Getting Help
- **Documentation**: Comprehensive documentation and examples
- **Community**: Active community support
- **Issues**: GitHub issue tracking
- **Discussions**: Community discussions and Q&A

### Contributing
- **Code Standards**: Follow PEP 8 and project guidelines
- **Testing**: Include comprehensive tests
- **Documentation**: Update documentation for changes
- **Review Process**: Code review and approval process

### License
This project is licensed under the MIT License. See LICENSE file for details.

---

**Note**: This documentation is continuously updated. For the latest version, please check the project repository. 