#!/usr/bin/env python3
"""
Test script for OCR functionality
"""

import requests
import json
import os
from PIL import Image, ImageDraw, ImageFont
import io


def create_test_pdf():
    """Create a test PDF with Persian text for OCR testing"""
    try:
        # Create a simple image with Persian text
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)

        # Add Persian text (simulating a legal document)
        text = """
        قرارداد نمونه خدمات نرم‌افزاری
        
        این قرارداد بین طرفین ذیل منعقد می‌گردد:
        
        ۱. طرف اول: شرکت توسعه نرم‌افزار
        ۲. طرف دوم: سازمان حقوقی
        
        موضوع قرارداد: توسعه سیستم مدیریت اسناد حقوقی
        
        مدت قرارداد: ۱۲ ماه
        مبلغ قرارداد: ۵۰۰ میلیون تومان
        
        شرایط و مقررات:
        - تحویل مرحله‌ای نرم‌افزار
        - پشتیبانی فنی ۲۴ ساعته
        - آموزش کاربران
        - مستندسازی کامل
        
        امضا:
        طرف اول: _________________
        طرف دوم: _________________
        تاریخ: ۱۴۰۴/۰۵/۱۰
        """

        # Try to use a font that supports Persian
        try:
            # Use a default font
            font = ImageFont.load_default()
        except:
            font = None

        # Draw text
        draw.text((50, 50), text, fill='black', font=font)

        # Save as PDF
        img.save('test_persian_document.pdf', 'PDF', resolution=300.0)
        print("✅ Test PDF created: test_persian_document.pdf")
        return True

    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return False


def test_ocr_endpoint():
    """Test the OCR endpoint"""
    try:
        # Check if test PDF exists
        if not os.path.exists('test_persian_document.pdf'):
            print("📄 Creating test PDF...")
            if not create_test_pdf():
                return False

        print("🔄 Testing OCR endpoint...")

        # Upload PDF to OCR endpoint
        url = "http://127.0.0.1:8000/api/test-ocr"

        with open('test_persian_document.pdf', 'rb') as f:
            files = {'file': ('test_persian_document.pdf',
                              f, 'application/pdf')}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            result = response.json()
            print("✅ OCR test successful!")
            print(f"📄 File processed: {result.get('filename')}")
            print(f"📄 Total pages: {result.get('total_pages')}")
            print(f"📄 Language: {result.get('language')}")
            print(f"📄 Model used: {result.get('model_used')}")
            print(f"📄 Success: {result.get('success')}")

            # Show extracted text (first 200 characters)
            full_text = result.get('full_text', '')
            if full_text:
                print(
                    f"📄 Extracted text (first 200 chars): {full_text[:200]}...")
            else:
                print("⚠️ No text extracted")

            return True
        else:
            print(f"❌ OCR test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing OCR endpoint: {e}")
        return False


def test_all_endpoints():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        "/",
        "/api/dashboard-summary",
        "/api/documents",
        "/api/charts-data",
        "/api/ai-suggestions",
        "/api/ai-training-stats"
    ]

    print("🧪 Testing all API endpoints...")

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting OCR and API Tests")
    print("=" * 50)

    # Test all endpoints
    test_all_endpoints()
    print("\n" + "=" * 50)

    # Test OCR functionality
    test_ocr_endpoint()

    print("\n" + "=" * 50)
    print("✅ Test completed!")
