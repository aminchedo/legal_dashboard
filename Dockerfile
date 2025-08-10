# استفاده از Python 3.11+ برای سازگاری
FROM python:3.11-slim

# نصب dependencies سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# کپی requirements و نصب packages
COPY requirements.txt .

# بروزرسانی pip و نصب پکیج‌ها
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# کپی کد اپلیکیشن
COPY . .

# تنظیمات environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# expose port
EXPOSE 8000

# اجرای اپلیکیشن
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
