#!/usr/bin/env python3
"""
Legal Dashboard App Entry Point
===============================

Entry point for Hugging Face Spaces deployment.
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment (Hugging Face Spaces sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Start the FastAPI application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info"
    )
