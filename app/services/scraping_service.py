"""
Advanced Web Scraping Service
=============================

Production-grade web scraping service with multiple strategies, async processing,
and comprehensive error handling for the Legal Dashboard OCR system.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time
from pydantic import BaseModel, Field
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class ScrapingStrategy(Enum):
    """Available scraping strategies"""
    GENERAL = "general"
    LEGAL_DOCUMENTS = "legal_documents"
    NEWS_ARTICLES = "news_articles"
    ACADEMIC_PAPERS = "academic_papers"
    GOVERNMENT_SITES = "government_sites"
    CUSTOM = "custom"


class ProcessingStatus(Enum):
    """Processing status for scraped items"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RATED = "rated"


@dataclass
class ScrapedItem:
    """Data structure for scraped items"""
    id: str
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    source_url: str
    rating_score: float = 0.0
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    strategy_used: ScrapingStrategy = ScrapingStrategy.GENERAL
    content_hash: str = ""
    word_count: int = 0
    language: str = "unknown"
    domain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['processing_status'] = self.processing_status.value
        data['strategy_used'] = self.strategy_used.value
        return data


class ScrapingJob(BaseModel):
    """Scraping job configuration"""
    job_id: str
    urls: List[str]
    strategy: ScrapingStrategy = ScrapingStrategy.GENERAL
    keywords: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    max_depth: int = 1
    delay_between_requests: float = 1.0
    timeout: int = 30
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0


class ScrapingService:
    """Advanced web scraping service with multiple strategies"""

    def __init__(self, db_path: str = "legal_documents.db"):
        self.db_path = db_path
        self.active_jobs: Dict[str, ScrapingJob] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database tables for scraping data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create scraped_items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scraped_items (
                        id TEXT PRIMARY KEY,
                        url TEXT NOT NULL,
                        title TEXT,
                        content TEXT,
                        metadata TEXT,
                        timestamp TEXT,
                        source_url TEXT,
                        rating_score REAL DEFAULT 0.0,
                        processing_status TEXT DEFAULT 'pending',
                        error_message TEXT,
                        strategy_used TEXT,
                        content_hash TEXT,
                        word_count INTEGER DEFAULT 0,
                        language TEXT DEFAULT 'unknown',
                        domain TEXT
                    )
                """)

                # Create scraping_jobs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scraping_jobs (
                        job_id TEXT PRIMARY KEY,
                        urls TEXT,
                        strategy TEXT,
                        keywords TEXT,
                        content_types TEXT,
                        max_depth INTEGER DEFAULT 1,
                        delay_between_requests REAL DEFAULT 1.0,
                        timeout INTEGER DEFAULT 30,
                        created_at TEXT,
                        status TEXT DEFAULT 'pending',
                        total_items INTEGER DEFAULT 0,
                        completed_items INTEGER DEFAULT 0,
                        failed_items INTEGER DEFAULT 0
                    )
                """)

                conn.commit()
                logger.info("✅ Scraping database initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize scraping database: {e}")

    async def start_session(self):
        """Start aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"scrape_job_{timestamp}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"

    def _generate_item_id(self, url: str) -> str:
        """Generate unique item ID based on URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"item_{timestamp}_{url_hash[:8]}"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for deduplication"""
        return hashlib.md5(content.encode()).hexdigest()

    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def _detect_language(self, text: str) -> str:
        """Simple language detection (can be enhanced)"""
        # Simple Persian detection
        persian_chars = re.findall(r'[\u0600-\u06FF]', text)
        if len(persian_chars) > len(text) * 0.3:
            return "persian"
        return "english"

    async def scrape_url(self, url: str, strategy: ScrapingStrategy, job_id: str) -> Optional[ScrapedItem]:
        """Scrape a single URL with specified strategy"""
        try:
            await self.start_session()

            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(
                        f"Failed to fetch {url}: Status {response.status}")
                    return None

                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    logger.info(f"Skipping non-HTML content: {url}")
                    return None

                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract content based on strategy
                title, content = await self._extract_content_by_strategy(soup, strategy)

                if not content or len(content.strip()) < 50:
                    logger.warning(f"Insufficient content from {url}")
                    return None

                # Create scraped item
                item_id = self._generate_item_id(url)
                domain = self._extract_domain(url)
                content_hash = self._calculate_content_hash(content)
                word_count = self._count_words(content)
                language = self._detect_language(content)

                item = ScrapedItem(
                    id=item_id,
                    url=url,
                    title=title or "No Title",
                    content=content,
                    metadata={
                        'content_type': content_type,
                        'response_time': response.headers.get('server-timing', ''),
                        'encoding': response.encoding,
                        'job_id': job_id
                    },
                    timestamp=datetime.now(timezone.utc),
                    source_url=url,
                    strategy_used=strategy,
                    content_hash=content_hash,
                    word_count=word_count,
                    language=language,
                    domain=domain,
                    processing_status=ProcessingStatus.COMPLETED
                )

                # Store in database
                await self._store_scraped_item(item)

                logger.info(
                    f"✅ Successfully scraped {url} ({word_count} words)")
                return item

        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping {url}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def _extract_content_by_strategy(self, soup: BeautifulSoup, strategy: ScrapingStrategy) -> tuple[str, str]:
        """Extract content based on scraping strategy"""
        title = ""
        content = ""

        try:
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()

            if strategy == ScrapingStrategy.LEGAL_DOCUMENTS:
                # Focus on legal document content
                legal_selectors = [
                    'article', '.legal-content', '.document-content',
                    '.legal-text', '.document-text', 'main'
                ]
                for selector in legal_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = ' '.join([elem.get_text().strip()
                                           for elem in elements])
                        break

                if not content:
                    # Fallback to body content
                    body = soup.find('body')
                    if body:
                        content = body.get_text().strip()

            elif strategy == ScrapingStrategy.NEWS_ARTICLES:
                # Focus on news article content
                news_selectors = [
                    'article', '.article-content', '.news-content',
                    '.story-content', '.post-content', 'main'
                ]
                for selector in news_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = ' '.join([elem.get_text().strip()
                                           for elem in elements])
                        break

                if not content:
                    # Fallback to body content
                    body = soup.find('body')
                    if body:
                        content = body.get_text().strip()

            elif strategy == ScrapingStrategy.ACADEMIC_PAPERS:
                # Focus on academic content
                academic_selectors = [
                    '.abstract', '.content', '.paper-content',
                    'article', '.research-content', 'main'
                ]
                for selector in academic_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = ' '.join([elem.get_text().strip()
                                           for elem in elements])
                        break

                if not content:
                    # Fallback to body content
                    body = soup.find('body')
                    if body:
                        content = body.get_text().strip()

            else:
                # General strategy - extract all text
                body = soup.find('body')
                if body:
                    content = body.get_text().strip()

            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()

        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            content = ""

        return title, content

    async def _store_scraped_item(self, item: ScrapedItem):
        """Store scraped item in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO scraped_items 
                    (id, url, title, content, metadata, timestamp, source_url, 
                     rating_score, processing_status, error_message, strategy_used,
                     content_hash, word_count, language, domain)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.id, item.url, item.title, item.content,
                    json.dumps(item.metadata), item.timestamp.isoformat(),
                    item.source_url, item.rating_score, item.processing_status.value,
                    item.error_message, item.strategy_used.value, item.content_hash,
                    item.word_count, item.language, item.domain
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing scraped item: {e}")

    async def start_scraping_job(self, urls: List[str], strategy: ScrapingStrategy = ScrapingStrategy.GENERAL,
                                 keywords: Optional[List[str]] = None, content_types: Optional[List[str]] = None,
                                 max_depth: int = 1, delay: float = 1.0) -> str:
        """Start a new scraping job"""
        job_id = self._generate_job_id()

        job = ScrapingJob(
            job_id=job_id,
            urls=urls,
            strategy=strategy,
            keywords=keywords,
            content_types=content_types,
            max_depth=max_depth,
            delay_between_requests=delay,
            total_items=len(urls)
        )

        self.active_jobs[job_id] = job

        # Store job in database
        await self._store_job(job)

        # Start scraping in background
        asyncio.create_task(self._execute_scraping_job(job))

        logger.info(f"🚀 Started scraping job {job_id} with {len(urls)} URLs")
        return job_id

    async def _execute_scraping_job(self, job: ScrapingJob):
        """Execute scraping job asynchronously"""
        try:
            job.status = "processing"
            await self._update_job_status(job)

            for i, url in enumerate(job.urls):
                try:
                    # Add delay between requests
                    if i > 0 and job.delay_between_requests > 0:
                        await asyncio.sleep(job.delay_between_requests)

                    item = await self.scrape_url(url, job.strategy, job.job_id)

                    if item:
                        job.completed_items += 1
                    else:
                        job.failed_items += 1

                    await self._update_job_status(job)

                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
                    job.failed_items += 1
                    await self._update_job_status(job)

            job.status = "completed"
            await self._update_job_status(job)
            logger.info(f"✅ Completed scraping job {job.job_id}")

        except Exception as e:
            logger.error(f"❌ Error in scraping job {job.job_id}: {e}")
            job.status = "failed"
            await self._update_job_status(job)

    async def _store_job(self, job: ScrapingJob):
        """Store job in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO scraping_jobs 
                    (job_id, urls, strategy, keywords, content_types, max_depth,
                     delay_between_requests, timeout, created_at, status,
                     total_items, completed_items, failed_items)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.job_id, json.dumps(job.urls), job.strategy.value,
                    json.dumps(job.keywords) if job.keywords else None,
                    json.dumps(
                        job.content_types) if job.content_types else None,
                    job.max_depth, job.delay_between_requests, job.timeout,
                    job.created_at.isoformat(), job.status, job.total_items,
                    job.completed_items, job.failed_items
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing job: {e}")

    async def _update_job_status(self, job: ScrapingJob):
        """Update job status in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE scraping_jobs 
                    SET status = ?, completed_items = ?, failed_items = ?
                    WHERE job_id = ?
                """, (job.status, job.completed_items, job.failed_items, job.job_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating job status: {e}")

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scraping job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                'job_id': job.job_id,
                'status': job.status,
                'total_items': job.total_items,
                'completed_items': job.completed_items,
                'failed_items': job.failed_items,
                'progress': (job.completed_items + job.failed_items) / job.total_items if job.total_items > 0 else 0,
                'created_at': job.created_at.isoformat(),
                'strategy': job.strategy.value
            }
        return None

    async def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all scraping jobs"""
        jobs = []
        for job in self.active_jobs.values():
            jobs.append(await self.get_job_status(job.job_id))
        return [job for job in jobs if job is not None]

    async def get_scraped_items(self, job_id: Optional[str] = None,
                                limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scraped items with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = """
                    SELECT id, url, title, content, metadata, timestamp, source_url,
                           rating_score, processing_status, error_message, strategy_used,
                           content_hash, word_count, language, domain
                    FROM scraped_items
                """
                params = []

                if job_id:
                    query += " WHERE metadata LIKE ?"
                    params.append(f'%"job_id": "{job_id}"%')

                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    item = {
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        # Truncate content
                        'content': row[3][:500] + "..." if len(row[3]) > 500 else row[3],
                        'metadata': json.loads(row[4]) if row[4] else {},
                        'timestamp': row[5],
                        'source_url': row[6],
                        'rating_score': row[7],
                        'processing_status': row[8],
                        'error_message': row[9],
                        'strategy_used': row[10],
                        'content_hash': row[11],
                        'word_count': row[12],
                        'language': row[13],
                        'domain': row[14]
                    }
                    items.append(item)

                return items

        except Exception as e:
            logger.error(f"Error retrieving scraped items: {e}")
            return []

    async def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total items
                cursor.execute("SELECT COUNT(*) FROM scraped_items")
                total_items = cursor.fetchone()[0]

                # Items by status
                cursor.execute("""
                    SELECT processing_status, COUNT(*) 
                    FROM scraped_items 
                    GROUP BY processing_status
                """)
                status_counts = dict(cursor.fetchall())

                # Items by language
                cursor.execute("""
                    SELECT language, COUNT(*) 
                    FROM scraped_items 
                    GROUP BY language
                """)
                language_counts = dict(cursor.fetchall())

                # Average rating
                cursor.execute(
                    "SELECT AVG(rating_score) FROM scraped_items WHERE rating_score > 0")
                avg_rating = cursor.fetchone()[0] or 0

                # Active jobs
                active_jobs = len(
                    [j for j in self.active_jobs.values() if j.status == "processing"])

                return {
                    'total_items': total_items,
                    'status_distribution': status_counts,
                    'language_distribution': language_counts,
                    'average_rating': round(avg_rating, 2),
                    'active_jobs': active_jobs,
                    'total_jobs': len(self.active_jobs)
                }

        except Exception as e:
            logger.error(f"Error getting scraping statistics: {e}")
            return {}

    async def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed jobs"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            # Remove old jobs from memory
            jobs_to_remove = []
            for job_id, job in self.active_jobs.items():
                if job.status in ["completed", "failed"] and job.created_at < cutoff_date:
                    jobs_to_remove.append(job_id)

            for job_id in jobs_to_remove:
                del self.active_jobs[job_id]

            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")

        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
