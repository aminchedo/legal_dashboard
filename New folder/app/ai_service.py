"""
AI Service for Legal Dashboard
=============================
* Updated with specific Gemini prompts for document analysis and search query parsing.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any
import httpx

# --- Existing AIScoringEngine Class ---
class AIScoringEngine:
    def __init__(self):
        logger.info("Initialized AIScoringEngine")
    # ... (Your existing methods for scoring, category prediction, etc.) ...

# --- GeminiLegalService Class ---
class GeminiLegalService:
    def __init__(self):
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key="
        self.headers = {'Content-Type': 'application/json'}
        logger.info("Initialized GeminiLegalService")

    async def _call_gemini_api(self, prompt: str, is_json_output: bool = False) -> Dict[str, Any]:
        """Private method to make an asynchronous call to the Gemini API."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if is_json_output:
            payload["generationConfig"] = {
                "responseMimeType": "application/json"
            }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")
                raise

    def _parse_gemini_response(self, response: Dict) -> str:
        """Safely parses the text content from a Gemini API response."""
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "پاسخی از سرویس هوشمند دریافت نشد."

    async def analyze_legal_document(self, document_text: str) -> str:
        """
        Generates a structured analysis of a legal document using Gemini.
        """
        prompt = f"""
        شما یک دستیار حقوقی متخصص هستید. سند حقوقی زیر را به زبان فارسی تحلیل کرده و یک گزارش ساختاریافته در فرمت Markdown ارائه دهید.
        گزارش باید شامل بخش‌های زیر باشد:
        ### خلاصه سند
        یک خلاصه کوتاه و دقیق از محتوای اصلی سند.
        ### نوع سند
        نوع سند را مشخص کنید (مثلا: قرارداد اجاره، رای دادگاه، دادخواست، قانون).
        ### طرفین اصلی
        اشخاص حقیقی یا حقوقی اصلی درگیر در سند را لیست کنید.
        ### تعهدات و نکات کلیدی
        مهم‌ترین تعهدات، مبالغ، تاریخ‌ها و شروط را به صورت لیست بیان کنید.
        ### کلمات کلیدی پیشنهادی
        ۵ کلمه کلیدی مناسب برای بایگانی و جستجوی این سند پیشنهاد دهید.

        متن سند:
        ---
        {document_text[:8000]}
        ---
        """
        response_json = await self._call_gemini_api(prompt)
        return self._parse_gemini_response(response_json)

    async def parse_search_query(self, query: str) -> Dict[str, Any]:
        """
        Parses a natural language search query into a structured JSON of filters using Gemini.
        """
        prompt = f"""
        شما یک موتور درک زبان طبیعی هستید که درخواست‌های جستجوی حقوقی به زبان فارسی را به فیلترهای JSON تبدیل می‌کنید.
        درخواست کاربر را تحلیل کرده و یک آبجکت JSON با فیلدهای زیر برگردانید:
        - "keywords": (string) کلمات کلیدی اصلی برای جستجوی متنی.
        - "category": (string) یکی از این مقادیر اگر در متن مشخص بود: ["قراردادها", "دادخواست‌ها", "احکام قضایی", "آرای دیوان", "قوانین", "سایر"].
        - "date_from": (string) تاریخ شروع در فرمت YYYY-MM-DD.
        - "date_to": (string) تاریخ پایان در فرمت YYYY-MM-DD.
        - "min_quality": (float) حداقل امتیاز کیفیت اگر مشخص شده بود (عددی بین 0.0 تا 10.0).
        - "sort": (string) یکی از این مقادیر: ["relevance", "date_desc", "date_asc", "quality_desc"].

        مثال:
        ورودی: "آرای دیوان عدالت در خصوص شهرداری در سال گذشته"
        خروجی: {{"keywords": "دیوان عدالت شهرداری", "category": "آرای دیوان", "date_from": "2024-08-05", "date_to": "2025-08-04", "sort": "relevance"}}

        ورودی: "قراردادهای اجاره با کیفیت بالای ۸"
        خروجی: {{"keywords": "قرارداد اجاره", "category": "قراردادها", "min_quality": 8.0, "sort": "quality_desc"}}
        
        فقط آبجکت JSON را بدون هیچ متن اضافی برگردان.

        درخواست کاربر: "{query}"
        """
        response_json = await self._call_gemini_api(prompt, is_json_output=True)
        parsed_text = self._parse_gemini_response(response_json)
        try:
            return json.loads(parsed_text)
        except json.JSONDecodeError:
            logger.error(f"Gemini did not return valid JSON for query parsing: {parsed_text}")
            # Fallback to simple keyword search
            return {"keywords": query, "sort": "relevance"}

# Instantiate the services
ai_scoring_engine = AIScoringEngine()
gemini_service = GeminiLegalService()
