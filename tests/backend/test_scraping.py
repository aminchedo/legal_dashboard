"""
Tests for Web Scraping Functionality
====================================

Comprehensive test suite for scraping service and API endpoints.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup

from app.services.scraping_service import (
    ScrapingService,
    ScrapingRequest,
    ScrapedContent,
    scraping_service
)
from app.api.scraping import router
from app.main import app


class TestScrapingService:
    """Test cases for ScrapingService"""

    def setup_method(self):
        """Setup for each test method"""
        self.service = ScrapingService()
        self.sample_html = """
        <html>
        <head>
            <title>Test Legal Document</title>
            <meta name="description" content="Test legal content">
        </head>
        <body>
            <main>
                <article>
                    <h1>قرارداد نمونه</h1>
                    <p>این یک قرارداد نمونه است که برای تست استفاده می‌شود.</p>
                    <p>ماده 1: تعاریف</p>
                    <p>ماده 2: موضوع قرارداد</p>
                </article>
            </main>
            <nav>
                <a href="https://example.com/page1">صفحه اول</a>
                <a href="https://example.com/page2">صفحه دوم</a>
            </nav>
            <img src="https://example.com/image.jpg" alt="تصویر">
        </body>
        </html>
        """

    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  متن   با   فاصله‌های   اضافی  \n\nو خط جدید  "
        cleaned = self.service._clean_text(dirty_text)

        assert cleaned == "متن با فاصله‌های اضافی و خط جدید"

    def test_extract_metadata(self):
        """Test metadata extraction"""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        metadata = self.service._extract_metadata(soup, "https://example.com")

        assert metadata['title'] == 'Test Legal Document'
        assert metadata['meta_description'] == 'Test legal content'
        assert metadata['domain'] == 'example.com'
        assert 'scraped_at' in metadata

    def test_extract_legal_content(self):
        """Test legal content extraction"""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        content = self.service._extract_legal_content(soup)

        assert 'قرارداد نمونه' in content
        assert 'ماده 1: تعاریف' in content
        assert 'ماده 2: موضوع قرارداد' in content
        assert 'صفحه اول' not in content  # Navigation should be excluded

    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        assert self.service.validate_url("https://gov.ir")
        assert self.service.validate_url("https://court.gov.ir")
        assert self.service.validate_url("https://example.com")

        # Invalid URLs
        assert not self.service.validate_url("not-a-url")
        assert not self.service.validate_url("ftp://example.com")
        assert not self.service.validate_url("")

    def test_get_scraping_stats(self):
        """Test scraping service statistics"""
        stats = self.service.get_scraping_stats()

        assert stats['service'] == 'Legal Dashboard Scraping Service'
        assert stats['version'] == '1.0.0'
        assert 'synchronous_scraping' in stats['supported_features']
        assert 'asynchronous_scraping' in stats['supported_features']
        assert 'legal_patterns' in stats

    @patch('requests.Session.get')
    def test_scrape_sync_success(self, mock_get):
        """Test successful synchronous scraping"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = self.sample_html.encode('utf-8')
        mock_get.return_value = mock_response

        request = ScrapingRequest(url="https://example.com")
        result = self.service.scrape_sync(request)

        assert result.url == "https://example.com"
        assert result.status_code == 200
        assert result.title == "Test Legal Document"
        assert result.text_content is not None
        assert len(result.text_content) > 0

    @patch('requests.Session.get')
    def test_scrape_sync_error(self, mock_get):
        """Test synchronous scraping with error"""
        # Mock error response
        mock_get.side_effect = Exception("Connection error")

        request = ScrapingRequest(url="https://example.com")

        with pytest.raises(Exception):
            self.service.scrape_sync(request)

    @patch('aiohttp.ClientSession.get')
    @patch('aiohttp.ClientSession.__aenter__')
    @patch('aiohttp.ClientSession.__aexit__')
    def test_scrape_async_success(self, mock_exit, mock_enter, mock_get):
        """Test successful asynchronous scraping"""
        # Mock async response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(
            return_value=self.sample_html.encode('utf-8'))
        mock_get.return_value.__aenter__.return_value = mock_response
        mock_enter.return_value = AsyncMock()
        mock_exit.return_value = AsyncMock()

        request = ScrapingRequest(url="https://example.com")

        # Run async test
        async def test_async():
            result = await self.service.scrape_async(request)
            assert result.url == "https://example.com"
            assert result.status_code == 200
            assert result.title == "Test Legal Document"
            assert result.text_content is not None

        asyncio.run(test_async())


class TestScrapingAPI:
    """Test cases for scraping API endpoints"""

    def setup_method(self):
        """Setup for each test method"""
        self.client = TestClient(app)

    def test_scrape_endpoint_success(self):
        """Test successful scraping via API"""
        with patch('app.services.scraping_service.scraping_service.scrape_async') as mock_scrape:
            # Mock successful scraping
            mock_scraped_content = ScrapedContent(
                url="https://example.com",
                title="Test Document",
                text_content="Test content",
                status_code=200,
                content_length=1000,
                scraped_at=datetime.now(),
                processing_time=1.5
            )
            mock_scrape.return_value = mock_scraped_content

            response = self.client.post("/api/scrape", json={
                "url": "https://example.com",
                "extract_text": True,
                "extract_metadata": True,
                "timeout": 30
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Content scraped successfully"
            assert data["data"]["url"] == "https://example.com"

    def test_scrape_endpoint_invalid_url(self):
        """Test scraping with invalid URL"""
        response = self.client.post("/api/scrape", json={
            "url": "not-a-valid-url",
            "extract_text": True
        })

        assert response.status_code == 200  # Returns error in response body
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_scrape_stats_endpoint(self):
        """Test scraping statistics endpoint"""
        response = self.client.get("/api/scrape/stats")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "supported_features" in data

    def test_scrape_history_endpoint(self):
        """Test scraping history endpoint"""
        response = self.client.get("/api/scrape/history")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "scraped_documents" in data["data"]

    def test_validate_url_endpoint(self):
        """Test URL validation endpoint"""
        # Test valid URL
        response = self.client.get("/api/scrape/validate?url=https://gov.ir")
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

        # Test invalid URL
        response = self.client.get("/api/scrape/validate?url=invalid-url")
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False

    def test_delete_scraped_document_endpoint(self):
        """Test delete scraped document endpoint"""
        response = self.client.delete("/api/scrape/1")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Document 1 deleted successfully" in data["message"]

    def test_batch_scrape_endpoint(self):
        """Test batch scraping endpoint"""
        with patch('app.services.scraping_service.scraping_service.scrape_async') as mock_scrape:
            # Mock successful scraping for multiple URLs
            mock_scraped_content = ScrapedContent(
                url="https://example.com",
                title="Test Document",
                text_content="Test content",
                status_code=200,
                content_length=1000,
                scraped_at=datetime.now(),
                processing_time=1.5
            )
            mock_scrape.return_value = mock_scraped_content

            response = self.client.post("/api/scrape/batch", json=[
                "https://example1.com",
                "https://example2.com"
            ])

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_urls"] == 2
            assert data["successful"] == 2
            assert data["failed"] == 0


class TestScrapingIntegration:
    """Integration tests for scraping functionality"""

    def test_scraping_service_integration(self):
        """Test integration between scraping service and API"""
        service = ScrapingService()

        # Test that service can be instantiated
        assert service is not None

        # Test that service has required methods
        assert hasattr(service, 'scrape_sync')
        assert hasattr(service, 'scrape_async')
        assert hasattr(service, 'validate_url')
        assert hasattr(service, 'get_scraping_stats')

    def test_scraping_request_model(self):
        """Test ScrapingRequest model validation"""
        # Valid request
        request = ScrapingRequest(
            url="https://example.com",
            extract_text=True,
            extract_links=False,
            timeout=30
        )
        assert request.url == "https://example.com"
        assert request.extract_text is True
        assert request.extract_links is False
        assert request.timeout == 30

    def test_scraped_content_model(self):
        """Test ScrapedContent model"""
        content = ScrapedContent(
            url="https://example.com",
            title="Test Title",
            text_content="Test content",
            status_code=200,
            content_length=1000,
            scraped_at=datetime.now(),
            processing_time=1.5
        )

        assert content.url == "https://example.com"
        assert content.title == "Test Title"
        assert content.text_content == "Test content"
        assert content.status_code == 200
        assert content.content_length == 1000
        assert content.processing_time == 1.5


if __name__ == "__main__":
    pytest.main([__file__])
