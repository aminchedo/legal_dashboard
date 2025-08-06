# ────────────────
# Stage 1: Builder
# ────────────────
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ────────────────
# Stage 2: Production
# ────────────────
FROM python:3.10-slim

# Create non-root user with specific UID/GID for compatibility
RUN groupadd -g 1000 appuser && useradd -r -u 1000 -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create all necessary directories with proper permissions
RUN mkdir -p \
    /app/data \
    /app/database \
    /app/cache \
    /app/logs \
    /app/uploads \
    /app/backups \
    /tmp/app_fallback \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser /tmp/app_fallback \
    && chmod -R 755 /app \
    && chmod -R 777 /tmp/app_fallback

# Copy application files with proper ownership
COPY --chown=appuser:appuser . .

# Make startup script executable if exists
RUN if [ -f start.sh ]; then chmod +x start.sh; fi

# Environment variables
ENV PYTHONPATH=/app
ENV DATABASE_DIR=/app/data
ENV DATABASE_PATH=/app/data/legal_documents.db
ENV TRANSFORMERS_CACHE=/app/cache
ENV HF_HOME=/app/cache
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Switch to non-root user BEFORE any file operations
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

# Default CMD with error handling
CMD ["sh", "-c", "python -c 'import os; os.makedirs(\"/app/data\", exist_ok=True)' && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]