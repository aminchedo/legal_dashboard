# 🚀 راهنمای استقرار - Deployment Guide

## 📋 فهرست مطالب

1. [استقرار روی Hugging Face Spaces](#hugging-face-spaces)
2. [استقرار با Docker](#docker-deployment)
3. [استقرار محلی](#local-deployment)
4. [استقرار روی سرور](#server-deployment)
5. [تنظیمات پیشرفته](#advanced-configuration)
6. [نظارت و نگهداری](#monitoring-maintenance)

---

## 🤗 Hugging Face Spaces

### مرحله ۱: ایجاد Space

۱. به [Hugging Face Spaces](https://huggingface.co/spaces) بروید
۲. روی "Create new Space" کلیک کنید
۳. تنظیمات زیر را انتخاب کنید:
   - **Owner**: حساب کاربری شما
   - **Space name**: `legal-dashboard`
   - **License**: MIT
   - **SDK**: Gradio
   - **Space hardware**: CPU (Basic)

### مرحله ۲: آپلود فایل‌ها

```bash
# کلون کردن Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/legal-dashboard
cd legal-dashboard

# کپی کردن فایل‌های پروژه
cp -r /path/to/legal-dashboard/* .

# اضافه کردن فایل‌ها به Git
git add .
git commit -m "Initial deployment of Legal Dashboard"
git push
```

### مرحله ۳: تنظیم متغیرهای محیطی

در تنظیمات Space، متغیرهای زیر را اضافه کنید:

```bash
# متغیرهای اصلی
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=7860

# امنیت
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# پایگاه داده
DATABASE_DIR=/tmp/legal_dashboard/data
TRANSFORMERS_CACHE=/tmp/cache
HF_HOME=/tmp/cache

# اسکرپینگ
SCRAPING_DELAY=2.0
SCRAPING_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=5

# رتبه‌بندی
RATING_BATCH_SIZE=10
RATING_CONFIDENCE_THRESHOLD=0.7
```

### مرحله ۴: راه‌اندازی

Space به طور خودکار راه‌اندازی می‌شود. برای بررسی وضعیت:

```bash
# بررسی لاگ‌ها
curl https://YOUR_USERNAME-legal-dashboard.hf.space/api/health

# پاسخ مورد انتظار:
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "scraping": "healthy",
    "rating": "healthy"
  }
}
```

---

## 🐳 Docker Deployment

### مرحله ۱: آماده‌سازی

```bash
# کلون کردن پروژه
git clone <repository-url>
cd legal-dashboard

# ساخت image
docker build -t legal-dashboard:latest .
```

### مرحله ۲: اجرا با Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  legal-dashboard:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_DIR=/app/data
      - TRANSFORMERS_CACHE=/app/cache
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

```bash
# اجرا
docker-compose up -d

# بررسی وضعیت
docker-compose ps
docker-compose logs -f legal-dashboard
```

### مرحله ۳: اجرا با Docker فقط

```bash
# اجرای مستقیم
docker run -d \
  --name legal-dashboard \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e JWT_SECRET_KEY=your-secret-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/cache:/app/cache \
  legal-dashboard:latest

# بررسی وضعیت
docker logs legal-dashboard
```

---

## 💻 Local Deployment

### مرحله ۱: نصب پیش‌نیازها

```bash
# نصب Python 3.10+
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# یا با pyenv
pyenv install 3.10.0
pyenv global 3.10.0
```

### مرحله ۲: راه‌اندازی محیط

```bash
# کلون کردن پروژه
git clone <repository-url>
cd legal-dashboard

# ایجاد محیط مجازی
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt
```

### مرحله ۳: تنظیم متغیرهای محیطی

```bash
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش فایل .env
nano .env
```

محتوای فایل `.env`:

```bash
# تنظیمات اصلی
ENVIRONMENT=development
LOG_LEVEL=DEBUG
PORT=8000

# امنیت
JWT_SECRET_KEY=your-development-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# پایگاه داده
DATABASE_DIR=./data
DATABASE_URL=sqlite:///./data/legal_documents.db

# کش
TRANSFORMERS_CACHE=./cache
HF_HOME=./cache
REDIS_URL=redis://localhost:6379

# اسکرپینگ
SCRAPING_DELAY=1.0
SCRAPING_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=3

# رتبه‌بندی
RATING_BATCH_SIZE=5
RATING_CONFIDENCE_THRESHOLD=0.7
```

### مرحله ۴: اجرا

```bash
# اجرای اصلی
python run.py

# یا اجرای مستقیم FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# یا اجرای Gradio
python app.py
```

---

## 🖥️ Server Deployment

### مرحله ۱: آماده‌سازی سرور

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب پیش‌نیازها
sudo apt install -y python3.10 python3.10-venv python3.10-dev \
  nginx redis-server supervisor git curl

# نصب Docker (اختیاری)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### مرحله ۲: راه‌اندازی پروژه

```bash
# ایجاد کاربر
sudo useradd -m -s /bin/bash legal-dashboard
sudo usermod -aG docker legal-dashboard

# کلون کردن پروژه
sudo -u legal-dashboard git clone <repository-url> /home/legal-dashboard/app
cd /home/legal-dashboard/app

# راه‌اندازی محیط
sudo -u legal-dashboard python3.10 -m venv venv
sudo -u legal-dashboard /home/legal-dashboard/app/venv/bin/pip install -r requirements.txt
```

### مرحله ۳: تنظیم Nginx

```nginx
# /etc/nginx/sites-available/legal-dashboard
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/legal-dashboard/app/static/;
        expires 30d;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# فعال‌سازی سایت
sudo ln -s /etc/nginx/sites-available/legal-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### مرحله ۴: تنظیم Supervisor

```ini
# /etc/supervisor/conf.d/legal-dashboard.conf
[program:legal-dashboard]
command=/home/legal-dashboard/app/venv/bin/python run.py
directory=/home/legal-dashboard/app
user=legal-dashboard
autostart=true
autorestart=true
stderr_logfile=/var/log/legal-dashboard/err.log
stdout_logfile=/var/log/legal-dashboard/out.log
environment=ENVIRONMENT="production",DATABASE_DIR="/home/legal-dashboard/data"
```

```bash
# ایجاد دایرکتوری لاگ
sudo mkdir -p /var/log/legal-dashboard
sudo chown legal-dashboard:legal-dashboard /var/log/legal-dashboard

# راه‌اندازی Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start legal-dashboard
```

### مرحله ۵: تنظیم SSL (اختیاری)

```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت گواهی SSL
sudo certbot --nginx -d your-domain.com

# تنظیم تمدید خودکار
sudo crontab -e
# اضافه کردن خط زیر:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ⚙️ Advanced Configuration

### تنظیمات پایگاه داده

```python
# config.py - تنظیمات پیشرفته پایگاه داده
DATABASE_CONFIG = {
    "sqlite": {
        "path": "/app/data/legal_documents.db",
        "timeout": 30,
        "check_same_thread": False
    },
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "database": "legal_dashboard",
        "user": "legal_user",
        "password": "secure_password"
    }
}
```

### تنظیمات کش

```python
# تنظیمات Redis
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": None,
    "max_connections": 20,
    "retry_on_timeout": True
}

# تنظیمات کش محلی
CACHE_CONFIG = {
    "ttl": 3600,  # 1 hour
    "max_size": 1000,
    "eviction_policy": "lru"
}
```

### تنظیمات امنیت

```python
# تنظیمات CORS
CORS_CONFIG = {
    "allow_origins": ["https://your-domain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"],
}

# تنظیمات Rate Limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 100,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
}
```

### تنظیمات لاگینگ

```python
# تنظیمات لاگینگ پیشرفته
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/legal-dashboard/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed"
        }
    },
    "loggers": {
        "app": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False
        }
    }
}
```

---

## 📊 Monitoring & Maintenance

### نظارت عملکرد

```bash
# بررسی وضعیت سیستم
curl http://localhost:8000/api/health

# بررسی آمار تفصیلی
curl http://localhost:8000/api/system/statistics

# بررسی لاگ‌ها
tail -f /var/log/legal-dashboard/app.log
```

### نگهداری پایگاه داده

```bash
# پشتیبان‌گیری
sqlite3 /app/data/legal_documents.db ".backup '/backup/legal_docs_$(date +%Y%m%d).db'"

# بهینه‌سازی
sqlite3 /app/data/legal_documents.db "VACUUM;"
sqlite3 /app/data/legal_documents.db "ANALYZE;"
```

### نظارت منابع

```bash
# بررسی استفاده از حافظه
free -h

# بررسی استفاده از CPU
top -p $(pgrep -f "legal-dashboard")

# بررسی فضای دیسک
df -h

# بررسی اتصالات شبکه
netstat -tulpn | grep :8000
```

### به‌روزرسانی سیستم

```bash
# به‌روزرسانی کد
cd /home/legal-dashboard/app
git pull origin main

# به‌روزرسانی وابستگی‌ها
source venv/bin/activate
pip install -r requirements.txt

# راه‌اندازی مجدد
sudo supervisorctl restart legal-dashboard
```

### پاکسازی داده‌های قدیمی

```bash
# حذف لاگ‌های قدیمی
find /var/log/legal-dashboard -name "*.log" -mtime +30 -delete

# حذف فایل‌های کش قدیمی
find /app/cache -name "*.tmp" -mtime +7 -delete

# پاکسازی پایگاه داده
sqlite3 /app/data/legal_documents.db "DELETE FROM scraped_items WHERE timestamp < datetime('now', '-90 days');"
```

---

## 🚨 Troubleshooting

### مشکلات رایج

#### ۱. خطای مجوز فایل
```bash
# حل مشکل
sudo chown -R legal-dashboard:legal-dashboard /home/legal-dashboard
sudo chmod -R 755 /home/legal-dashboard
```

#### ۲. خطای اتصال به پایگاه داده
```bash
# بررسی وجود فایل
ls -la /app/data/legal_documents.db

# ایجاد دایرکتوری
sudo mkdir -p /app/data
sudo chown legal-dashboard:legal-dashboard /app/data
```

#### ۳. خطای حافظه
```bash
# افزایش swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### ۴. خطای پورت
```bash
# بررسی پورت‌های استفاده شده
sudo netstat -tulpn | grep :8000

# تغییر پورت در فایل .env
PORT=8001
```

### لاگ‌های مفید

```bash
# لاگ‌های اپلیکیشن
tail -f /var/log/legal-dashboard/app.log

# لاگ‌های Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# لاگ‌های Supervisor
sudo supervisorctl tail legal-dashboard
```

---

## 📞 پشتیبانی

### اطلاعات تماس
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@legal-dashboard.com
- **Documentation**: [README.md](./README.md)

### منابع مفید
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Supervisor Documentation](http://supervisord.org/)

---

**🏛️ Legal Dashboard** - راهنمای کامل استقرار و نگهداری