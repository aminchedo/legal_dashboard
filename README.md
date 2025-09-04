# 🏛️ Legal Dashboard - داشبورد حقوقی ایران

[![Hugging Face Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Persian](https://img.shields.io/badge/Persian-RTL-orange.svg)](https://github.com)
[![AI](https://img.shields.io/badge/AI-Powered-red.svg)](https://github.com)

## 📋 معرفی سیستم

**Legal Dashboard** یک سیستم جامع مدیریت و تحلیل اسناد حقوقی ایرانی است که با استفاده از هوش مصنوعی و پردازش زبان طبیعی، اسناد حقوقی فارسی را جمع‌آوری، تحلیل و رتبه‌بندی می‌کند.

### 🌟 ویژگی‌های کلیدی

- **🔍 جمع‌آوری خودکار**: اسکرپینگ خودکار از ۱۵+ منبع حقوقی ایرانی
- **🤖 تحلیل هوشمند**: پردازش اسناد با الگوریتم‌های پیشرفته AI
- **📊 رتبه‌بندی ۶ معیاری**: ارزیابی کیفیت بر اساس ۶ معیار مختلف
- **🌐 رابط کاربری چندگانه**: وب و Gradio برای Hugging Face Spaces
- **📱 پشتیبانی چندزبانه**: فارسی و انگلیسی
- **☁️ استقرار چندسکویی**: Docker، HF Spaces، و محلی
- **⚡ پردازش غیرهمزمان**: بهینه‌سازی عملکرد با async/await
- **🔒 امنیت پیشرفته**: احراز هویت و رمزنگاری داده‌ها

## 🏗️ معماری سیستم

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scraping      │───▶│   Rating         │───▶│   Database      │
│   Service       │    │   Service        │    │   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Cache          │    │   AI Service    │
│   Updates       │    │   Service        │    │   Analysis      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔧 اجزای اصلی

#### **۱. سرویس اسکرپینگ (ScrapingService)**
- استراتژی‌های مختلف اسکرپینگ (اسناد حقوقی، اخبار، مقالات علمی، سایت‌های دولتی)
- پردازش غیرهمزمان با aiohttp
- تشخیص زبان (فارسی/انگلیسی)
- ارزیابی کیفیت محتوا

#### **۲. سرویس رتبه‌بندی (RatingService)**
- **اعتبار منبع (۲۵٪)**: ارزیابی اعتبار سایت‌های حقوقی
- **کامل بودن محتوا (۲۵٪)**: بررسی جامعیت اطلاعات
- **دقت OCR (۲۰٪)**: تحلیل کیفیت متن استخراج شده
- **تازگی داده (۱۵٪)**: ارزیابی به‌روز بودن اطلاعات
- **مرتبط بودن محتوا (۱۰٪)**: بررسی ارتباط با موضوعات حقوقی
- **کیفیت فنی (۵٪)**: ارزیابی ساختار و فرمت

#### **۳. سرویس پایگاه داده (DatabaseService)**
- SQLite با جستجوی تمام متن (FTS5)
- نسخه‌گذاری اسناد و ردیابی تغییرات
- بهینه‌سازی عملکرد با ایندکس‌ها
- قابلیت‌های جستجوی پیشرفته

#### **۴. سرویس هوش مصنوعی (AIService)**
- استخراج کلیدواژه‌های حقوقی فارسی
- تشخیص موجودیت‌ها (نام‌ها، شرکت‌ها، تاریخ‌ها، مبالغ)
- طبقه‌بندی اسناد به دسته‌های حقوقی
- تحلیل احساسات در اسناد حقوقی
- تشخیص شباهت بر اساس TF-IDF

## 📊 منابع داده حقوقی

### 🏛️ منابع رسمی دولت
| منبع | آدرس | نوع محتوا | اعتبار | به‌روزرسانی |
|------|------|-----------|--------|-------------|
| سامانه حقوقی دولت | https://www.dotic.ir | قوانین و مقررات | ۹۵٪ | روزانه |
| مرکز پژوهش‌های مجلس | https://rc.majlis.ir | پژوهش‌های حقوقی | ۹۰٪ | هفتگی |
| میزان آنلاین | https://www.mizanonline.ir | اخبار حقوقی | ۹۰٪ | روزانه |

### 📰 خبرگزاری‌های رسمی
| منبع | آدرس | نوع محتوا | اعتبار | به‌روزرسانی |
|------|------|-----------|--------|-------------|
| خبرگزاری جمهوری اسلامی | https://www.irna.ir | اخبار حقوقی | ۹۰٪ | ساعتی |
| خبرگزاری مهر | https://www.mehrnews.ir | اخبار حقوقی | ۸۰٪ | ساعتی |
| خبرگزاری تسنیم | https://www.tasnimnews.com | اخبار حقوقی | ۸۰٪ | ساعتی |
| خبرگزاری فارس | https://www.farsnews.ir | اخبار حقوقی | ۸۰٪ | ساعتی |

### 🏢 نهادهای قضایی
| منبع | آدرس | نوع محتوا | اعتبار | به‌روزرسانی |
|------|------|-----------|--------|-------------|
| دادایران | https://www.dadiran.ir | آرای قضایی | ۸۰٪ | روزانه |
| بانک اطلاعات حقوقی | https://www.lawdata.ir | پایگاه داده حقوقی | ۸۵٪ | هفتگی |
| بانک قوانین | https://www.lawbank.ir | قوانین و مقررات | ۸۵٪ | هفتگی |

### 📚 منابع دانشگاهی
| منبع | آدرس | نوع محتوا | اعتبار | به‌روزرسانی |
|------|------|-----------|--------|-------------|
| مرکز تحقیقات راهبردی | https://www.rrk.ir | پژوهش‌های حقوقی | ۸۰٪ | ماهانه |
| مجله حقوق ایران | https://www.ijlr.ir | مقالات علمی | ۷۵٪ | فصلانه |

### 🔍 منابع عمومی
| منبع | آدرس | نوع محتوا | اعتبار | به‌روزرسانی |
|------|------|-----------|--------|-------------|
| پایگاه حقوق | https://www.hoghoogh.com | منابع عمومی | ۶۰٪ | هفتگی |
| قانون | https://www.qanoon.ir | مرجع حقوقی | ۷۰٪ | هفتگی |
| انتخاب | https://www.entekhab.ir | اخبار عمومی | ۷۰٪ | ساعتی |

## 🚀 راه‌اندازی سریع

### گزینه ۱: Hugging Face Spaces (توصیه شده برای دمو)

۱. **این Space را Fork کنید** یا یک Space جدید ایجاد کنید
۲. **تمام فایل‌ها را آپلود کنید** به Space خود
۳. **متغیرهای محیطی را تنظیم کنید** در تنظیمات Space:
   ```bash
   JWT_SECRET_KEY=your-super-secret-key-here
   DATABASE_DIR=/tmp/legal_dashboard/data
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   TRANSFORMERS_CACHE=/app/cache
   HF_HOME=/app/cache
   PORT=7860
   ```
۴. **Space را راه‌اندازی کنید** - به طور خودکار شروع می‌شود

**اطلاعات ورود دمو:**
- نام کاربری: `admin`
- رمز عبور: `admin123`

### گزینه ۲: استقرار Docker

```bash
# کلون کردن مخزن
git clone <your-repo-url>
cd legal-dashboard

# ساخت و اجرا
docker-compose up --build

# یا فقط با Docker
docker build -t legal-dashboard .
docker run -p 8000:8000 legal-dashboard
```

### گزینه ۳: توسعه محلی

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
export DATABASE_DIR=./data
export LOG_LEVEL=DEBUG
export JWT_SECRET_KEY=your-secret-key

# اجرای برنامه
python app.py
```

## 📚 مستندات API

### 🔐 احراز هویت
```bash
# ورود به سیستم
POST /api/auth/login
{
    "username": "admin",
    "password": "admin123"
}

# پاسخ
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### 📄 مدیریت اسناد
```bash
# آپلود سند
POST /api/documents/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

# دریافت لیست اسناد
GET /api/documents?page=1&limit=20
Authorization: Bearer <token>

# جستجوی اسناد
GET /api/documents/search?q=قانون+مدنی
Authorization: Bearer <token>
```

### 🔍 اسکرپینگ
```bash
# شروع اسکرپینگ دستی
POST /api/system/start-scraping
Authorization: Bearer <token>

# وضعیت اسکرپینگ
GET /api/scraping/status
Authorization: Bearer <token>

# آمار اسکرپینگ
GET /api/scraping/statistics
Authorization: Bearer <token>
```

### 📊 رتبه‌بندی
```bash
# شروع رتبه‌بندی دستی
POST /api/system/start-rating
Authorization: Bearer <token>

# آمار رتبه‌بندی
GET /api/rating/summary
Authorization: Bearer <token>

# آیتم‌های بدون رتبه
GET /api/rating/unrated?limit=50
Authorization: Bearer <token>
```

### 📈 تحلیل و گزارش
```bash
# گزارش جامع
GET /api/reports/comprehensive
Authorization: Bearer <token>

# آمار عملکرد
GET /api/analytics/performance
Authorization: Bearer <token>

# تحلیل روند
GET /api/analytics/trends?period=monthly
Authorization: Bearer <token>
```

### 🔧 مدیریت سیستم
```bash
# وضعیت سلامت سیستم
GET /api/health

# وضعیت جامع سیستم
GET /api/system/status

# آمار عملکرد
GET /api/system/statistics
```

## 🎯 معیارهای رتبه‌بندی

### 📊 معیارهای ارزیابی (۶ معیار)

#### ۱. اعتبار منبع (۲۵٪)
- **منابع رسمی دولت**: ۹۵٪ اعتبار
- **خبرگزاری‌های رسمی**: ۹۰٪ اعتبار  
- **نهادهای قضایی**: ۸۰٪ اعتبار
- **منابع دانشگاهی**: ۷۵٪ اعتبار
- **منابع عمومی**: ۶۰٪ اعتبار

#### ۲. کامل بودن محتوا (۲۵٪)
- **متن کامل**: ۱۰۰٪ امتیاز
- **متن ناقص**: ۵۰٪ امتیاز
- **فقط عنوان**: ۱۰٪ امتیاز
- **بدون محتوا**: ۰٪ امتیاز

#### ۳. دقت OCR (۲۰٪)
- **کیفیت عالی**: ۹۰-۱۰۰٪ امتیاز
- **کیفیت خوب**: ۷۰-۸۹٪ امتیاز
- **کیفیت متوسط**: ۵۰-۶۹٪ امتیاز
- **کیفیت ضعیف**: زیر ۵۰٪ امتیاز

#### ۴. تازگی داده (۱۵٪)
- **امروز**: ۱۰۰٪ امتیاز
- **هفته گذشته**: ۸۰٪ امتیاز
- **ماه گذشته**: ۶۰٪ امتیاز
- **سال گذشته**: ۳۰٪ امتیاز
- **قدیمی‌تر**: ۱۰٪ امتیاز

#### ۵. مرتبط بودن محتوا (۱۰٪)
- **کاملاً مرتبط**: ۱۰۰٪ امتیاز
- **نسبتاً مرتبط**: ۷۰٪ امتیاز
- **کم‌تر مرتبط**: ۴۰٪ امتیاز
- **نامرتبط**: ۰٪ امتیاز

#### ۶. کیفیت فنی (۵٪)
- **ساختار مناسب**: ۱۰۰٪ امتیاز
- **ساختار متوسط**: ۶۰٪ امتیاز
- **ساختار ضعیف**: ۲۰٪ امتیاز

### 🏆 سطوح رتبه‌بندی
- **عالی (Excellent)**: ۸۰-۱۰۰٪
- **خوب (Good)**: ۶۰-۷۹٪
- **متوسط (Average)**: ۴۰-۵۹٪
- **ضعیف (Poor)**: ۲۰-۳۹٪
- **بدون رتبه (Unrated)**: زیر ۲۰٪

## 🔧 مشخصات فنی

### 💻 نیازمندی‌های سیستم
- **Python**: 3.10+
- **RAM**: حداقل ۲GB، توصیه ۴GB
- **CPU**: حداقل ۲ هسته، توصیه ۴ هسته
- **فضای ذخیره**: حداقل ۵GB
- **شبکه**: اتصال اینترنت پایدار

### 📊 عملکرد هدف
- **اسکرپینگ روزانه**: ۵۰+ سند
- **دقت رتبه‌بندی**: بالای ۸۵٪
- **زمان پاسخ API**: زیر ۲ ثانیه
- **در دسترس بودن**: بالای ۹۹٪
- **استفاده حافظه**: زیر ۱GB

### 🔒 امنیت
- **احراز هویت JWT**: بله
- **رمزنگاری داده‌ها**: بله
- **اعتبارسنجی ورودی**: بله
- **محدودیت نرخ درخواست**: بله
- **محافظت XSS**: بله

### 🌐 پشتیبانی زبانی
- **فارسی**: کامل (RTL)
- **انگلیسی**: کامل
- **تشخیص خودکار زبان**: بله
- **تبدیل تاریخ شمسی**: بله
- **تبدیل اعداد فارسی**: بله
# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم محیط
cp .env.example .env
# فایل .env را با تنظیمات خود ویرایش کنید

# اجرای اپلیکیشن
python run.py
# یا رابط‌های خاص:
python app.py          # رابط Gradio
uvicorn app.main:app   # فقط FastAPI
```

## 📊 API Documentation

### نقاط پایانی اصلی

#### **مدیریت اسناد**
- `GET /api/documents` - دریافت لیست اسناد
- `POST /api/documents/upload` - آپلود سند جدید
- `GET /api/documents/{id}` - دریافت جزئیات سند
- `DELETE /api/documents/{id}` - حذف سند

#### **اسکرپینگ وب**
- `POST /api/scraping/start` - شروع اسکرپینگ
- `GET /api/scraping/status` - وضعیت اسکرپینگ
- `GET /api/scraping/items` - دریافت آیتم‌های اسکرپ شده
- `POST /api/scraping/stop` - توقف اسکرپینگ

#### **تحلیل و رتبه‌بندی**
- `GET /api/analytics/summary` - خلاصه تحلیلات
- `GET /api/rating/summary` - خلاصه رتبه‌بندی
- `POST /api/rating/evaluate/{id}` - ارزیابی مجدد سند

#### **مدیریت سیستم**
- `GET /api/health` - بررسی سلامت سیستم
- `GET /api/system/status` - وضعیت جامع سیستم
- `POST /api/system/start-scraping` - شروع دستی اسکرپینگ
- `POST /api/system/start-rating` - شروع دستی رتبه‌بندی

### مثال درخواست

```bash
# دریافت وضعیت سیستم
curl -X GET "http://localhost:8000/api/health"

# شروع اسکرپینگ
curl -X POST "http://localhost:8000/api/scraping/start" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.mizanonline.ir"], "strategy": "legal_documents"}'

# دریافت تحلیلات
curl -X GET "http://localhost:8000/api/analytics/summary"
```

## 📚 منابع حقوقی ایرانی

### منابع اصلی (اولویت بالا)

| نام | آدرس | نوع | استراتژی |
|-----|-------|-----|----------|
| میزان آنلاین | mizanonline.ir | اخبار حقوقی | legal_documents |
| سامانه حقوقی دولت | dotic.ir | دولتی | government_sites |
| مرکز پژوهش‌های مجلس | rc.majlis.ir | تحقیقاتی | academic_papers |
| بانک اطلاعات حقوقی | lawdata.ir | پایگاه داده | legal_documents |
| بانک قوانین | lawbank.ir | پایگاه قوانین | legal_documents |

### منابع ثانویه (اولویت متوسط)

| نام | آدرس | نوع | استراتژی |
|-----|-------|-----|----------|
| دادایران | dadiran.ir | قضایی | legal_documents |
| مرکز تحقیقات راهبردی | rrk.ir | تحقیقاتی | academic_papers |
| مجله حقوق ایران | ijlr.ir | آکادمیک | academic_papers |
| قانون | qanoon.ir | مرجع حقوقی | legal_documents |

### منابع عمومی (اولویت پایین)

| نام | آدرس | نوع | استراتژی |
|-----|-------|-----|----------|
| پایگاه حقوق | hoghoogh.com | عمومی حقوقی | legal_documents |

## 🔍 معیارهای رتبه‌بندی

### ۱. اعتبار منبع (۲۵٪ وزن)
- **عالی (۰.۹-۱.۰)**: سایت‌های رسمی دولتی (gov.ir, court.gov.ir)
- **خوب (۰.۷-۰.۹)**: سایت‌های خبری معتبر (irna.ir, isna.ir)
- **متوسط (۰.۵-۰.۷)**: سایت‌های حقوقی تخصصی
- **ضعیف (۰.۰-۰.۵)**: سایت‌های عمومی

### ۲. کامل بودن محتوا (۲۵٪ وزن)
- **عالی (۰.۹-۱.۰)**: بیش از ۱۰۰۰ کلمه، عنوان کامل، محتوای ساختاریافته
- **خوب (۰.۷-۰.۹)**: ۵۰۰-۱۰۰۰ کلمه، عنوان مناسب
- **متوسط (۰.۵-۰.۷)**: ۲۰۰-۵۰۰ کلمه، عنوان ساده
- **ضعیف (۰.۰-۰.۵)**: کمتر از ۲۰۰ کلمه، عنوان ناقص

### ۳. دقت OCR (۲۰٪ وزن)
- **عالی (۰.۹-۱.۰)**: متن کاملاً خوانا، بدون خطا
- **خوب (۰.۷-۰.۹)**: متن قابل خواندن، خطاهای جزئی
- **متوسط (۰.۵-۰.۷)**: متن قابل فهم، خطاهای متوسط
- **ضعیف (۰.۰-۰.۵)**: متن ناخوانا، خطاهای زیاد

### ۴. تازگی داده (۱۵٪ وزن)
- **عالی (۰.۹-۱.۰)**: کمتر از ۱ ماه
- **خوب (۰.۷-۰.۹)**: ۱-۶ ماه
- **متوسط (۰.۵-۰.۷)**: ۶ ماه - ۱ سال
- **ضعیف (۰.۰-۰.۵)**: بیش از ۱ سال

### ۵. مرتبط بودن محتوا (۱۰٪ وزن)
- **عالی (۰.۹-۱.۰)**: کاملاً مرتبط با موضوعات حقوقی
- **خوب (۰.۷-۰.۹)**: مرتبط با موضوعات حقوقی
- **متوسط (۰.۵-۰.۷)**: تا حدی مرتبط
- **ضعیف (۰.۰-۰.۵)**: غیرمرتبط

### ۶. کیفیت فنی (۵٪ وزن)
- **عالی (۰.۹-۱.۰)**: ساختار کامل، فرمت مناسب
- **خوب (۰.۷-۰.۹)**: ساختار مناسب
- **متوسط (۰.۵-۰.۷)**: ساختار ساده
- **ضعیف (۰.۰-۰.۵)**: ساختار ضعیف

## 🛠️ مشخصات فنی

### نیازمندی‌های سیستم
- **Python**: 3.10+
- **RAM**: حداقل ۲GB (توصیه شده ۴GB)
- **Storage**: حداقل ۵GB فضای آزاد
- **Network**: اتصال اینترنت پایدار

### عملکرد
- **زمان پاسخ API**: کمتر از ۲ ثانیه
- **دقت رتبه‌بندی**: بالای ۸۵٪
- **اسکرپینگ روزانه**: ۵۰+ سند
- **Uptime**: بالای ۹۹٪

### امنیت
- احراز هویت JWT
- رمزگذاری داده‌ها
- محافظت در برابر SQL Injection
- Rate Limiting
- CORS Configuration

## 📁 ساختار پروژه

```
legal-dashboard/
├── 🚀 استقرار و پیکربندی
│   ├── app.py                  # نقطه ورود HF Spaces
│   ├── run.py                  # اجراکننده جهانی
│   ├── config.py               # مدیریت پیکربندی
│   ├── Dockerfile              # پیکربندی Docker
│   ├── docker-compose.yml      # Docker Compose
│   ├── requirements.txt        # وابستگی‌ها
│   └── .env                    # متغیرهای محیطی
│
├── 🏗️ Backend (FastAPI)
│   ├── app/
│   │   ├── main.py             # اپلیکیشن FastAPI
│   │   ├── api/                # نقاط پایانی API
│   │   │   ├── auth.py         # احراز هویت
│   │   │   ├── documents.py    # مدیریت اسناد
│   │   │   ├── scraping.py     # اسکرپینگ وب
│   │   │   ├── analytics.py    # تحلیلات
│   │   │   └── websocket.py    # ارتباطات زنده
│   │   ├── services/           # منطق تجاری
│   │   │   ├── scraping_service.py   # سرویس اسکرپینگ
│   │   │   ├── rating_service.py     # سرویس رتبه‌بندی
│   │   │   ├── ai_service.py         # سرویس هوش مصنوعی
│   │   │   ├── database_service.py   # سرویس پایگاه داده
│   │   │   └── cache_service.py      # سرویس کش
│   │   └── models/             # مدل‌های داده
│
├── 📊 Frontend
│   ├── frontend/               # رابط کاربری وب
│   └── static/                 # فایل‌های استاتیک
│
└── 📚 مستندات
    ├── README.md               # این فایل
    ├── API.md                  # مستندات API
    └── DEPLOYMENT.md           # راهنمای استقرار
```

## 🔧 تنظیمات پیشرفته

### متغیرهای محیطی

```bash
# تنظیمات اصلی
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=7860

# پایگاه داده
DATABASE_DIR=/app/data
DATABASE_URL=sqlite:///legal_documents.db

# کش و حافظه
TRANSFORMERS_CACHE=/app/cache
HF_HOME=/app/cache
REDIS_URL=redis://localhost:6379

# امنیت
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# اسکرپینگ
SCRAPING_DELAY=2.0
SCRAPING_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=10

# رتبه‌بندی
RATING_BATCH_SIZE=20
RATING_CONFIDENCE_THRESHOLD=0.7
```

### تنظیمات Docker

```yaml
version: '3.8'
services:
  legal-dashboard:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_DIR=/app/data
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
    depends_on:
      - redis
```

## 📈 نظارت و نگهداری

### معیارهای موفقیت
- **اسکرپینگ موفق**: ۵۰+ سند روزانه
- **دقت رتبه‌بندی**: بالای ۸۵٪
- **زمان پاسخ API**: کمتر از ۲ ثانیه
- **Uptime سیستم**: بالای ۹۹٪
- **استفاده حافظه**: کمتر از ۱GB

### نظارت عملکرد
- نرخ موفقیت اسکرپینگ
- معیارهای دقت رتبه‌بندی
- عملکرد پایگاه داده
- الگوهای استفاده حافظه
- زمان پاسخ API
- ردیابی خطاها

## 🤝 مشارکت

### نحوه مشارکت
۱. پروژه را Fork کنید
۲. یک شاخه جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
۳. تغییرات خود را commit کنید (`git commit -m 'Add amazing feature'`)
۴. به شاخه push کنید (`git push origin feature/amazing-feature`)
۵. یک Pull Request ایجاد کنید

### استانداردهای کدنویسی
- استفاده از docstring برای تمام توابع
- تست‌نویسی برای کدهای جدید
- پیروی از PEP 8
- کامنت‌گذاری به فارسی برای بخش‌های پیچیده

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل `LICENSE` را مطالعه کنید.

## 📞 پشتیبانی

### راه‌های ارتباطی
- **Issues**: برای گزارش باگ‌ها و درخواست ویژگی‌ها
- **Discussions**: برای سوالات و بحث‌ها
- **Email**: برای ارتباط مستقیم

### منابع مفید
- [مستندات FastAPI](https://fastapi.tiangolo.com/)
- [راهنمای Hugging Face Spaces](https://huggingface.co/docs/hub/spaces)
- [مستندات Docker](https://docs.docker.com/)

---

**🏛️ Legal Dashboard** - جامع‌ترین سیستم مدیریت اسناد حقوقی ایرانی با هوش مصنوعی