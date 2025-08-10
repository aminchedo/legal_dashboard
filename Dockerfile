# استفاده از Python 3.11 کاملاً آپدیت
FROM python:3.11-slim

# نصب فقط ضروری‌ترین dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# کپی requirements
COPY requirements.txt .

# نصب پکیج‌ها بدون cache
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد
COPY . .

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# اجرا
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
