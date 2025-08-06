# Legal Dashboard OCR - Deployment Guide

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and run the application:**
   ```bash
   cd legal_dashboard_ocr
   docker-compose up --build
   ```

2. **Access the application:**
   - Open your browser and go to: `http://localhost:7860`
   - The application will be available on port 7860

### Using Docker directly

1. **Build the Docker image:**
   ```bash
   cd legal_dashboard_ocr
   docker build -t legal-dashboard-ocr .
   ```

2. **Run the container:**
   ```bash
   docker run -p 7860:7860 -v $(pwd)/data:/app/data -v $(pwd)/cache:/app/cache legal-dashboard-ocr
   ```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. **Check if the data directory exists:**
   ```bash
   docker exec -it <container_name> ls -la /app/data
   ```

2. **Create the data directory manually:**
   ```bash
   docker exec -it <container_name> mkdir -p /app/data
   docker exec -it <container_name> chmod 777 /app/data
   ```

3. **Test database connection:**
   ```bash
   docker exec -it <container_name> python debug_container.py
   ```

### OCR Model Issues

If OCR models fail to load:

1. **Check available models:**
   The application will automatically try these models in order:
   - `microsoft/trocr-base-stage1`
   - `microsoft/trocr-base-handwritten`
   - `microsoft/trocr-small-stage1`
   - `microsoft/trocr-small-handwritten`

2. **Set Hugging Face token (optional):**
   ```bash
   export HF_TOKEN=your_huggingface_token
   docker run -e HF_TOKEN=$HF_TOKEN -p 7860:7860 legal-dashboard-ocr
   ```

### Container Logs

To view container logs:
```bash
docker-compose logs -f
```

Or for direct Docker:
```bash
docker logs <container_name> -f
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/app/data/legal_dashboard.db` | SQLite database path |
| `TRANSFORMERS_CACHE` | `/app/cache` | Hugging Face cache directory |
| `HF_HOME` | `/app/cache` | Hugging Face home directory |
| `HF_TOKEN` | (not set) | Hugging Face authentication token |

## Volume Mounts

The application uses these volume mounts for persistent data:

- `./data:/app/data` - Database and uploaded files
- `./cache:/app/cache` - Hugging Face model cache

## Health Check

The application includes a health check endpoint:
- URL: `http://localhost:7860/health`
- Returns status of OCR, database, and AI services

## Common Issues and Solutions

### Issue: "unable to open database file"
**Solution:**
1. Ensure the data directory exists and has proper permissions
2. Check if the volume mount is working correctly
3. Run the debug script: `docker exec -it <container> python debug_container.py`

### Issue: OCR models fail to load
**Solution:**
1. The application will automatically fall back to basic text extraction
2. Check internet connectivity for model downloads
3. Set HF_TOKEN if you have Hugging Face access

### Issue: Container fails to start
**Solution:**
1. Check Docker logs: `docker logs <container_name>`
2. Ensure port 7860 is not already in use
3. Verify Docker has enough resources (memory/disk)

## Development

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 7860
   ```

### Testing

1. **Test database connection:**
   ```bash
   python test_db_connection.py
   ```

2. **Test container environment:**
   ```bash
   docker run --rm legal-dashboard-ocr python debug_container.py
   ```

## Performance Optimization

1. **Model caching:** The application caches Hugging Face models in `/app/cache`
2. **Database optimization:** SQLite database is optimized for concurrent access
3. **Memory usage:** Consider increasing Docker memory limits for large models

## Security Considerations

1. **Database security:** SQLite database is stored in a volume mount
2. **API security:** Consider adding authentication for production use
3. **File uploads:** Implement file size limits and type validation

## Monitoring

The application provides:
- Health check endpoint: `/health`
- Real-time logs via Docker
- System metrics in the database

## Support

For issues not covered in this guide:
1. Check the application logs
2. Run the debug script
3. Verify Docker and system resources 