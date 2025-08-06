# 📚 API Documentation - مستندات API

## 🏛️ Legal Dashboard API

این مستندات شامل تمام نقاط پایانی API برای سیستم Legal Dashboard است.

### 🔗 Base URL
```
Production: https://your-hf-space.hf.space
Local: http://localhost:8000
```

### 📋 Authentication
اکثر نقاط پایانی نیاز به احراز هویت دارند. از JWT Token استفاده کنید:

```bash
# دریافت توکن
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# استفاده از توکن
curl -X GET "http://localhost:8000/api/documents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔐 Authentication API

### POST /api/auth/login
**ورود کاربر**

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### POST /api/auth/register
**ثبت‌نام کاربر جدید**

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 2
}
```

---

## 📄 Document Management API

### GET /api/documents
**دریافت لیست اسناد**

**Query Parameters:**
- `page`: شماره صفحه (پیش‌فرض: 1)
- `limit`: تعداد آیتم در هر صفحه (پیش‌فرض: 20)
- `search`: جستجو در عنوان و محتوا
- `category`: فیلتر بر اساس دسته‌بندی
- `rating_min`: حداقل امتیاز
- `rating_max`: حداکثر امتیاز

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "title": "قانون تجارت",
      "content": "متن قانون تجارت...",
      "category": "commercial_law",
      "rating_score": 0.85,
      "upload_date": "2024-01-15T10:30:00Z",
      "file_size": 1024000,
      "file_type": "pdf"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### POST /api/documents/upload
**آپلود سند جدید**

**Request (multipart/form-data):**
```
file: [binary file]
title: "عنوان سند"
category: "commercial_law"
description: "توضیحات سند"
```

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": "doc_456",
  "processing_status": "processing"
}
```

### GET /api/documents/{id}
**دریافت جزئیات سند**

**Response:**
```json
{
  "id": "doc_123",
  "title": "قانون تجارت",
  "content": "متن کامل قانون...",
  "category": "commercial_law",
  "rating_score": 0.85,
  "upload_date": "2024-01-15T10:30:00Z",
  "file_size": 1024000,
  "file_type": "pdf",
  "metadata": {
    "pages": 45,
    "language": "fa",
    "ocr_confidence": 0.92
  },
  "analysis": {
    "keywords": ["قانون", "تجارت", "شرکت"],
    "entities": ["شرکت سهامی", "سرمایه"],
    "sentiment": "neutral"
  }
}
```

### DELETE /api/documents/{id}
**حذف سند**

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## 🔍 Web Scraping API

### POST /api/scraping/start
**شروع اسکرپینگ**

**Request Body:**
```json
{
  "urls": [
    "https://www.mizanonline.ir",
    "https://www.dotic.ir"
  ],
  "strategy": "legal_documents",
  "keywords": ["قانون", "مقررات", "دستورالعمل"],
  "max_depth": 2,
  "delay": 2.0
}
```

**Response:**
```json
{
  "job_id": "job_789",
  "status": "started",
  "message": "Scraping job started successfully"
}
```

### GET /api/scraping/status
**وضعیت اسکرپینگ**

**Response:**
```json
{
  "active_jobs": 2,
  "total_jobs": 15,
  "completed_jobs": 13,
  "failed_jobs": 0,
  "total_items_scraped": 1250,
  "last_scraping_time": "2024-01-15T14:30:00Z"
}
```

### GET /api/scraping/items
**دریافت آیتم‌های اسکرپ شده**

**Query Parameters:**
- `job_id`: فیلتر بر اساس job
- `limit`: تعداد آیتم (پیش‌فرض: 50)
- `offset`: شروع از (پیش‌فرض: 0)
- `rating_min`: حداقل امتیاز
- `source`: فیلتر بر اساس منبع

**Response:**
```json
{
  "items": [
    {
      "id": "item_123",
      "url": "https://www.mizanonline.ir/article/123",
      "title": "تغییرات جدید در قانون تجارت",
      "content": "متن مقاله...",
      "source_url": "https://www.mizanonline.ir",
      "rating_score": 0.78,
      "scraped_at": "2024-01-15T14:25:00Z",
      "word_count": 850,
      "language": "fa"
    }
  ],
  "total": 1250,
  "limit": 50,
  "offset": 0
}
```

### POST /api/scraping/stop
**توقف اسکرپینگ**

**Request Body:**
```json
{
  "job_id": "job_789"
}
```

**Response:**
```json
{
  "message": "Scraping job stopped successfully",
  "job_id": "job_789"
}
```

---

## 📊 Analytics API

### GET /api/analytics/summary
**خلاصه تحلیلات**

**Response:**
```json
{
  "total_documents": 1250,
  "total_scraped_items": 850,
  "average_rating": 0.72,
  "documents_by_category": {
    "commercial_law": 450,
    "civil_law": 320,
    "criminal_law": 280,
    "administrative_law": 200
  },
  "rating_distribution": {
    "excellent": 180,
    "good": 420,
    "average": 380,
    "poor": 270
  },
  "recent_activity": {
    "documents_uploaded_today": 15,
    "items_scraped_today": 25,
    "average_processing_time": "2.3s"
  }
}
```

### GET /api/analytics/trends
**روندها و آمار**

**Query Parameters:**
- `period`: دوره زمانی (daily, weekly, monthly)
- `start_date`: تاریخ شروع
- `end_date`: تاریخ پایان

**Response:**
```json
{
  "period": "monthly",
  "trends": [
    {
      "date": "2024-01-01",
      "documents_added": 45,
      "items_scraped": 120,
      "average_rating": 0.75
    },
    {
      "date": "2024-01-02",
      "documents_added": 52,
      "items_scraped": 135,
      "average_rating": 0.78
    }
  ]
}
```

### GET /api/analytics/keywords
**تحلیل کلیدواژه‌ها**

**Response:**
```json
{
  "top_keywords": [
    {
      "keyword": "قانون",
      "frequency": 1250,
      "average_rating": 0.82
    },
    {
      "keyword": "تجارت",
      "frequency": 890,
      "average_rating": 0.76
    }
  ],
  "keyword_trends": {
    "rising": ["قانون جدید", "مقررات"],
    "declining": ["قانون قدیم"]
  }
}
```

---

## ⭐ Rating API

### GET /api/rating/summary
**خلاصه رتبه‌بندی**

**Response:**
```json
{
  "total_rated": 1250,
  "average_score": 0.72,
  "rating_distribution": {
    "excellent": 180,
    "good": 420,
    "average": 380,
    "poor": 270
  },
  "criteria_breakdown": {
    "source_credibility": 0.78,
    "content_completeness": 0.75,
    "ocr_accuracy": 0.82,
    "data_freshness": 0.68,
    "content_relevance": 0.85,
    "technical_quality": 0.70
  }
}
```

### POST /api/rating/evaluate/{id}
**ارزیابی مجدد سند**

**Request Body:**
```json
{
  "evaluator": "manual",
  "notes": "ارزیابی دستی انجام شد"
}
```

**Response:**
```json
{
  "item_id": "item_123",
  "new_score": 0.85,
  "previous_score": 0.72,
  "criteria_scores": {
    "source_credibility": 0.90,
    "content_completeness": 0.85,
    "ocr_accuracy": 0.88,
    "data_freshness": 0.75,
    "content_relevance": 0.90,
    "technical_quality": 0.80
  },
  "confidence": 0.92,
  "evaluator": "manual"
}
```

### GET /api/rating/history/{id}
**تاریخچه رتبه‌بندی**

**Response:**
```json
{
  "item_id": "item_123",
  "history": [
    {
      "timestamp": "2024-01-15T14:30:00Z",
      "score": 0.85,
      "evaluator": "manual",
      "notes": "ارزیابی دستی"
    },
    {
      "timestamp": "2024-01-15T10:15:00Z",
      "score": 0.72,
      "evaluator": "auto",
      "notes": "ارزیابی خودکار"
    }
  ]
}
```

---

## 🔧 System Management API

### GET /api/health
**بررسی سلامت سیستم**

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "ocr": "healthy",
    "scraping": "healthy",
    "rating": "healthy",
    "background_tasks": "running"
  },
  "statistics": {
    "uptime": "2 days, 5 hours",
    "memory_usage": "512MB",
    "cpu_usage": "15%",
    "active_connections": 5
  },
  "version": "1.0.0"
}
```

### GET /api/system/status
**وضعیت جامع سیستم**

**Response:**
```json
{
  "system": {
    "status": "operational",
    "version": "1.0.0",
    "uptime": "2 days, 5 hours"
  },
  "scraping": {
    "active_jobs": 2,
    "total_jobs": 15,
    "background_running": true
  },
  "rating": {
    "total_rated": 1250,
    "average_score": 0.72,
    "background_running": true
  },
  "background_tasks": {
    "scraping": true,
    "rating": true
  }
}
```

### POST /api/system/start-scraping
**شروع دستی اسکرپینگ**

**Response:**
```json
{
  "message": "Scraping process started",
  "status": "success"
}
```

### POST /api/system/start-rating
**شروع دستی رتبه‌بندی**

**Response:**
```json
{
  "message": "Rating process started",
  "status": "success"
}
```

### GET /api/system/statistics
**آمار تفصیلی عملکرد**

**Response:**
```json
{
  "timestamp": "2024-01-15T15:00:00Z",
  "statistics": {
    "scraping": {
      "total_items": 1250,
      "success_rate": 0.95,
      "average_processing_time": "1.2s"
    },
    "rating": {
      "total_rated": 1250,
      "average_score": 0.72,
      "accuracy": 0.87
    },
    "database": {
      "total_documents": 1250,
      "storage_size": "256MB",
      "query_performance": "0.05s"
    }
  }
}
```

---

## 🔌 WebSocket API

### WebSocket Connection
**اتصال WebSocket برای به‌روزرسانی‌های زنده**

**URL:** `ws://localhost:8000/ws`

**Message Types:**

#### 1. Scraping Progress
```json
{
  "type": "scraping_progress",
  "job_id": "job_789",
  "progress": 75,
  "items_scraped": 150,
  "current_url": "https://www.mizanonline.ir"
}
```

#### 2. Rating Update
```json
{
  "type": "rating_update",
  "item_id": "item_123",
  "new_score": 0.85,
  "evaluator": "auto"
}
```

#### 3. System Health
```json
{
  "type": "system_health",
  "status": "healthy",
  "memory_usage": "512MB",
  "active_jobs": 2
}
```

---

## 🚨 Error Responses

### Standard Error Format
```json
{
  "error": "Error message in Persian",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "additional error details"
  },
  "timestamp": "2024-01-15T15:00:00Z"
}
```

### Common Error Codes
- `AUTH_REQUIRED`: نیاز به احراز هویت
- `INVALID_TOKEN`: توکن نامعتبر
- `PERMISSION_DENIED`: عدم دسترسی
- `RESOURCE_NOT_FOUND`: منبع یافت نشد
- `VALIDATION_ERROR`: خطای اعتبارسنجی
- `INTERNAL_ERROR`: خطای داخلی سرور

### Example Error Response
```json
{
  "error": "توکن احراز هویت نامعتبر است",
  "error_code": "INVALID_TOKEN",
  "details": {
    "expired_at": "2024-01-15T14:30:00Z"
  },
  "timestamp": "2024-01-15T15:00:00Z"
}
```

---

## 📝 Rate Limiting

### Limits
- **API Calls**: 100 requests per minute per user
- **File Uploads**: 10 files per hour per user
- **Scraping Jobs**: 5 jobs per hour per user

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1642248000
```

---

## 🔒 Security

### Authentication
- JWT tokens with 30-minute expiration
- Refresh tokens with 7-day expiration
- bcrypt password hashing

### CORS
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Data Protection
- SQL injection prevention
- XSS protection
- Input validation
- Secure file handling

---

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

**📚 برای اطلاعات بیشتر به [README.md](./README.md) مراجعه کنید.**