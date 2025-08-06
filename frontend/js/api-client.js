/**
 * Legal Dashboard API Client
 * =========================
 * 
 * JavaScript client for communicating with the Legal Dashboard backend API.
 * Handles all HTTP requests and data transformation between frontend and backend.
 */

class LegalDashboardAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
        this.apiBase = `${this.baseUrl}/api`;
        
        // Request interceptor for common headers
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic HTTP request handler with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
            
        } catch (error) {
            console.error(`API Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Health check - verify backend is running
     */
    async healthCheck() {
        return this.request('/health');
    }

    // ==================== DASHBOARD API ====================

    /**
     * Get dashboard summary statistics
     */
    async getDashboardSummary() {
        const response = await this.request('/dashboard/summary');
        return response.data;
    }

    /**
     * Get processing trends for charts
     */
    async getProcessingTrends(period = 'weekly') {
        const response = await this.request(`/dashboard/charts/processing-trends?period=${period}`);
        return response.data;
    }

    /**
     * Get status distribution for pie chart
     */
    async getStatusDistribution() {
        const response = await this.request('/dashboard/charts/status-distribution');
        return response.data;
    }

    /**
     * Get category distribution for pie chart
     */
    async getCategoryDistribution() {
        const response = await this.request('/dashboard/charts/category-distribution');
        return response.data;
    }

    // ==================== DOCUMENTS API ====================

    /**
     * Get paginated list of documents with filtering
     */
    async getDocuments(params = {}) {
        const searchParams = new URLSearchParams();
        
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                searchParams.append(key, value);
            }
        });
        
        const endpoint = `/documents/?${searchParams.toString()}`;
        return this.request(endpoint);
    }

    /**
     * Get single document by ID
     */
    async getDocument(documentId) {
        return this.request(`/documents/${documentId}`);
    }

    /**
     * Delete document by ID
     */
    async deleteDocument(documentId) {
        return this.request(`/documents/${documentId}`, {
            method: 'DELETE'
        });
    }

    // ==================== OCR API ====================

    /**
     * Upload files for OCR processing
     */
    async uploadFiles(files) {
        const formData = new FormData();
        
        // Add files to form data
        files.forEach(file => {
            formData.append('files', file);
        });

        return this.request('/ocr/upload', {
            method: 'POST',
            headers: {}, // Remove Content-Type to let browser set it for FormData
            body: formData
        });
    }

    /**
     * Extract text from PDF immediately (for testing)
     */
    async extractTextImmediate(file) {
        const formData = new FormData();
        formData.append('file', file);

        return this.request('/ocr/extract', {
            method: 'POST',
            headers: {},
            body: formData
        });
    }

    // ==================== SCRAPING API ====================

    /**
     * Scrape content from website
     */
    async scrapeWebsite(scrapingRequest) {
        return this.request('/scraping/scrape', {
            method: 'POST',
            body: JSON.stringify(scrapingRequest)
        });
    }

    /**
     * Get scraping history
     */
    async getScrapingHistory(skip = 0, limit = 50) {
        const response = await this.request(`/scraping/scrape/history?skip=${skip}&limit=${limit}`);
        return response.data;
    }

    // ==================== ANALYTICS API ====================

    /**
     * Calculate similarity between two documents
     */
    async calculateSimilarity(doc1Id, doc2Id) {
        const response = await this.request(`/analytics/similarity?doc1_id=${doc1Id}&doc2_id=${doc2Id}`);
        return response.data;
    }

    /**
     * Get quality analysis
     */
    async getQualityAnalysis() {
        const response = await this.request('/analytics/quality-analysis');
        return response.data;
    }

    /**
     * Get performance metrics
     */
    async getPerformanceMetrics() {
        const response = await this.request('/analytics/performance-metrics');
        return response.data;
    }
}

// ==================== DATA MODELS ====================

/**
 * Document model to match backend structure
 */
class DocumentModel {
    constructor(backendData) {
        this.id = backendData.id;
        this.filename = backendData.filename;
        this.original_filename = backendData.original_filename;
        this.file_size = backendData.file_size;
        this.file_path = backendData.file_path;
        this.category = backendData.category;
        this.quality_score = backendData.quality_score || 0;
        this.confidence_score = backendData.confidence_score || 0;
        this.status = backendData.status;
        this.created_at = backendData.created_at;
        this.processed_at = backendData.processed_at;
        this.ocr_text = backendData.ocr_text;
        this.summary = backendData.summary;
        this.keywords = backendData.keywords || [];
        this.extracted_entities = backendData.extracted_entities || [];
        this.processing_time = backendData.processing_time || 0;
        this.importance_score = backendData.importance_score || 0;
        this.similarity_scores = backendData.similarity_scores || {};
        this.legal_references = backendData.legal_references || [];
    }

    /**
     * Format file size for display
     */
    getFormattedFileSize() {
        return formatFileSize(this.file_size);
    }

    /**
     * Get creation date formatted for Persian locale
     */
    getFormattedDate() {
        return formatDate(this.created_at);
    }

    /**
     * Get quality class for styling
     */
    getQualityClass() {
        if (this.quality_score >= 8.5) return 'quality-excellent';
        if (this.quality_score >= 6.5) return 'quality-good';
        if (this.quality_score >= 4.5) return 'quality-average';
        return 'quality-poor';
    }

    /**
     * Get status text in Persian
     */
    getStatusText() {
        const statusMap = {
            'processed': 'پردازش شده',
            'processing': 'در حال پردازش',
            'uploaded': 'آپلود شده',
            'pending': 'در انتظار',
            'error': 'خطا'
        };
        return statusMap[this.status] || this.status;
    }

    /**
     * Get status icon
     */
    getStatusIcon() {
        const iconMap = {
            'processed': 'check-circle',
            'processing': 'spinner fa-spin',
            'uploaded': 'cloud-upload-alt',
            'pending': 'clock',
            'error': 'exclamation-triangle'
        };
        return iconMap[this.status] || 'question-circle';
    }
}

/**
 * Scraping result model
 */
class ScrapingResultModel {
    constructor(backendData) {
        this.success = backendData.success;
        this.url = backendData.url;
        this.title = backendData.title;
        this.content_length = backendData.content_length;
        this.processing_time = backendData.processing_time;
        this.data = backendData.data;
        this.error = backendData.error;
    }

    isSuccessful() {
        return this.success && !this.error;
    }

    getFormattedProcessingTime() {
        return `${this.processing_time.toFixed(2)} ثانیه`;
    }
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Format file size in bytes to human readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 بایت';
    const k = 1024;
    const sizes = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format date for Persian locale
 */
function formatDate(dateString) {
    if (!dateString) return 'نامشخص';
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', title = 'اعلان') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-${icons[type]}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button type="button" class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    toastContainer.appendChild(toast);

    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== GLOBAL API INSTANCE ====================

// Create global API instance
window.legalAPI = new LegalDashboardAPI();

// Test connection on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.legalAPI.healthCheck();
        console.log('✅ Backend connection successful');
    } catch (error) {
        console.warn('⚠️ Backend connection failed, using fallback mode:', error.message);
        showToast('اتصال به سرور برقرار نشد. حالت آفلاین فعال است.', 'warning', 'هشدار اتصال');
    }
});

console.log('🔗 Legal Dashboard API Client loaded');
