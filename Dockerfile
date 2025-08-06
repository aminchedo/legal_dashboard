# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_DIR=/app/data
ENV DATABASE_PATH=/app/data/legal_dashboard.db
ENV TRANSFORMERS_CACHE=/app/cache
ENV HF_HOME=/app/cache
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser appuser

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data \
    /app/cache \
    /app/logs \
    /app/uploads \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fs http://localhost:8000/api/health || exit 1

# Start command optimized for Hugging Face Spaces
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]