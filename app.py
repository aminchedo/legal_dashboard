import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as core_app

# ایجاد اپلیکیشن FastAPI
app = FastAPI(title="Legal Dashboard OCR", version="1.0.0")

# فعال کردن CORS برای دسترسی فرانت‌اند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اضافه کردن مسیرهای اصلی پروژه
app.mount("/", core_app)

# اجرای لوکال یا روی Hugging Face
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
