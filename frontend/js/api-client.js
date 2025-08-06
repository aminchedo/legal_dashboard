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

        // Error handling configuration
        this.retryConfig = {
            maxRetries: 3,
            retryDelay: 1000,
            retryableStatuses: [500, 502, 503, 504]
        };

        // Persian error messages
        this.errorMessages = {
            400: 'درخواست نامعتبر - لطفاً اطلاعات ورودی را بررسی کنید',
            401: 'دسترسی غیرمجاز - لطفاً وارد سیستم شوید',
            403: 'دسترسی مجاز نیست',
            404: 'صفحه یا منبع مورد نظر یافت نشد',
            408: 'زمان درخواست تمام شد',
            429: 'تعداد درخواست‌ها زیاد است - لطفاً کمی صبر کنید',
            500: 'خطای داخلی سرور',
            502: 'خطای ارتباط با سرور',
            503: 'سرویس در دسترس نیست',
            504: 'زمان اتصال به سرور تمام شد',
            'network': 'خطا در اتصال به شبکه',
            'timeout': 'زمان درخواست تمام شد',
            'unknown': 'خطای نامشخص رخ داده است'
        };

        // Offline mode storage
        this.offlineCache = new Map();
        this.offlineMode = false;

        // Performance optimization settings
        this.performanceConfig = {
            cacheExpiry: 5 * 60 * 1000, // 5 minutes default
            longCacheExpiry: 30 * 60 * 1000, // 30 minutes for static data
            batchSize: 50, // For paginated requests
            lazyLoadThreshold: 100, // Load more when 100px from bottom
            imageCompression: {
                maxWidth: 1200,
                maxHeight: 800,
                quality: 0.8
            }
        };

        // Request queue for batching
        this.requestQueue = [];
        this.batchTimer = null;
    }

    /**
     * Generic HTTP request handler with enhanced error handling and retry
     */
    async request(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const cacheKey = `${endpoint}_${JSON.stringify(options)}`;

        // Check offline mode first
        if (this.offlineMode && options.method !== 'POST') {
            const cachedData = this.getCachedData(cacheKey);
            if (cachedData) {
                console.log(`📦 Returning cached data for ${endpoint}`);
                return cachedData;
            }
        }

        const config = {
            timeout: 10000, // 10 second timeout
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            }
        };

        return this.executeWithRetry(async () => {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), config.timeout);

                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new APIError(response.status, await this.extractErrorMessage(response));
                }

                const contentType = response.headers.get('content-type');
                let data;

                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    data = await response.text();
                }

                // Cache successful GET requests
                if (config.method === 'GET' || !config.method) {
                    this.setCachedData(cacheKey, data);
                }

                // Reset offline mode on successful request
                if (this.offlineMode) {
                    this.offlineMode = false;
                    this.showNotification('اتصال برقرار شد', 'success');
                }

                return data;

            } catch (error) {
                console.error(`API Request failed: ${endpoint}`, error);

                if (error.name === 'AbortError') {
                    throw new APIError('timeout', this.errorMessages.timeout);
                }

                // Check for network errors
                if (!navigator.onLine || error.message.includes('Failed to fetch')) {
                    this.handleOfflineMode();
                    throw new APIError('network', this.errorMessages.network);
                }

                throw error;
            }
        }, endpoint);
    }

    /**
     * Execute request with retry mechanism
     */
    async executeWithRetry(operation, endpoint) {
        let lastError;

        for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;

                // Don't retry for certain error types
                if (error instanceof APIError &&
                    (error.status < 500 || !this.retryConfig.retryableStatuses.includes(error.status))) {
                    throw error;
                }

                if (attempt === this.retryConfig.maxRetries) {
                    console.error(`Max retries reached for ${endpoint}`);
                    break;
                }

                const delay = this.retryConfig.retryDelay * attempt;
                console.warn(`Retrying ${endpoint} in ${delay}ms (attempt ${attempt}/${this.retryConfig.maxRetries})`);

                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        throw lastError;
    }

    /**
     * Extract error message from response
     */
    async extractErrorMessage(response) {
        try {
            const errorData = await response.json();
            return errorData.detail || errorData.message || this.errorMessages[response.status] || this.errorMessages.unknown;
        } catch {
            return this.errorMessages[response.status] || this.errorMessages.unknown;
        }
    }

    /**
     * Handle offline mode
     */
    handleOfflineMode() {
        if (!this.offlineMode) {
            this.offlineMode = true;
            console.warn('🔌 Switching to offline mode');
            this.showNotification('اتصال قطع شده - حالت آفلاین فعال شد', 'warning', 5000);
        }
    }

    /**
     * Cache management
     */
    setCachedData(key, data, expiry = 5 * 60 * 1000) { // 5 minutes default
        this.offlineCache.set(key, {
            data: data,
            timestamp: Date.now(),
            expiry: Date.now() + expiry
        });
    }

    getCachedData(key) {
        const cached = this.offlineCache.get(key);
        if (!cached) return null;

        if (Date.now() > cached.expiry) {
            this.offlineCache.delete(key);
            return null;
        }

        return cached.data;
    }

    clearCache() {
        this.offlineCache.clear();
    }

    /**
     * Show notification (requires notifications.js)
     */
    showNotification(message, type = 'info', duration = 3000) {
        if (typeof showToast === 'function') {
            showToast(message, type, duration);
        } else if (window.dashboardCore && typeof window.dashboardCore.showPersianToast === 'function') {
            window.dashboardCore.showPersianToast(message, type, duration);
        } else {
            console.log(`Notification: ${message} (${type})`);
        }
    }

    /**
     * Enhanced caching with intelligent expiry
     */
    setCachedData(key, data, customExpiry = null) {
        const expiry = customExpiry || this.getOptimalCacheExpiry(key);

        this.offlineCache.set(key, {
            data: data,
            timestamp: Date.now(),
            expiry: Date.now() + expiry,
            accessCount: 0,
            lastAccess: Date.now()
        });

        // Clean up old cache entries
        this.cleanupCache();
    }

    getCachedData(key) {
        const cached = this.offlineCache.get(key);
        if (!cached) return null;

        if (Date.now() > cached.expiry) {
            this.offlineCache.delete(key);
            return null;
        }

        // Update access statistics
        cached.accessCount++;
        cached.lastAccess = Date.now();

        return cached.data;
    }

    /**
     * Get optimal cache expiry based on endpoint type
     */
    getOptimalCacheExpiry(key) {
        // Static/configuration data - cache longer
        if (key.includes('/health') || key.includes('/config') || key.includes('/categories')) {
            return this.performanceConfig.longCacheExpiry;
        }

        // Dynamic data - shorter cache
        if (key.includes('/documents') || key.includes('/dashboard/summary')) {
            return this.performanceConfig.cacheExpiry;
        }

        // Real-time data - very short cache
        if (key.includes('/scraping/status') || key.includes('/analytics/performance')) {
            return 60 * 1000; // 1 minute
        }

        return this.performanceConfig.cacheExpiry;
    }

    /**
     * Clean up expired cache entries
     */
    cleanupCache() {
        const now = Date.now();
        const maxCacheSize = 100; // Maximum cache entries

        // Remove expired entries
        for (const [key, cached] of this.offlineCache.entries()) {
            if (now > cached.expiry) {
                this.offlineCache.delete(key);
            }
        }

        // Remove least recently used entries if cache is too large
        if (this.offlineCache.size > maxCacheSize) {
            const entries = Array.from(this.offlineCache.entries());
            entries.sort((a, b) => a[1].lastAccess - b[1].lastAccess);

            const toRemove = entries.slice(0, entries.length - maxCacheSize);
            toRemove.forEach(([key]) => this.offlineCache.delete(key));
        }
    }

    /**
     * Batch multiple requests for efficiency
     */
    async batchRequest(requests) {
        const batchId = Date.now().toString();
        console.log(`🔄 Batching ${requests.length} requests (${batchId})`);

        try {
            const results = await Promise.allSettled(
                requests.map(req => this.request(req.endpoint, req.options))
            );

            const successful = results.filter(r => r.status === 'fulfilled').length;
            console.log(`✅ Batch ${batchId}: ${successful}/${requests.length} successful`);

            return results;
        } catch (error) {
            console.error(`❌ Batch ${batchId} failed:`, error);
            throw error;
        }
    }

    /**
     * Paginated data loading with lazy loading support
     */
    async loadPaginatedData(endpoint, options = {}) {
        const {
            page = 1,
            limit = this.performanceConfig.batchSize,
            onPageLoaded = null,
            loadAll = false
        } = options;

        const allData = [];
        let currentPage = page;
        let hasMore = true;

        while (hasMore) {
            try {
                const response = await this.request(endpoint, {
                    ...options,
                    method: 'GET'
                });

                const pageData = response.data || response.items || response;
                allData.push(...pageData);

                // Call callback for each page if provided
                if (onPageLoaded) {
                    onPageLoaded(pageData, currentPage);
                }

                // Check if there's more data
                hasMore = loadAll && pageData.length === limit;
                currentPage++;

                if (!loadAll) break; // Only load one page if not loading all

            } catch (error) {
                console.error(`Error loading page ${currentPage}:`, error);
                break;
            }
        }

        return allData;
    }

    /**
     * Image compression and optimization
     */
    async compressImage(file, options = {}) {
        const config = { ...this.performanceConfig.imageCompression, ...options };

        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // Calculate new dimensions
                let { width, height } = img;
                const aspectRatio = width / height;

                if (width > config.maxWidth) {
                    width = config.maxWidth;
                    height = width / aspectRatio;
                }

                if (height > config.maxHeight) {
                    height = config.maxHeight;
                    width = height * aspectRatio;
                }

                // Set canvas dimensions
                canvas.width = width;
                canvas.height = height;

                // Draw and compress
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(
                    blob => {
                        const compressedFile = new File([blob], file.name, {
                            type: file.type,
                            lastModified: Date.now()
                        });

                        console.log(`📷 Image compressed: ${formatFileSize(file.size)} → ${formatFileSize(compressedFile.size)}`);
                        resolve(compressedFile);
                    },
                    file.type,
                    config.quality
                );
            };

            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Lazy loading helper for infinite scroll
     */
    createLazyLoader(container, loadMoreCallback) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        loadMoreCallback();
                    }
                });
            },
            {
                root: container,
                rootMargin: `${this.performanceConfig.lazyLoadThreshold}px`,
                threshold: 0.1
            }
        );

        // Create sentinel element
        const sentinel = document.createElement('div');
        sentinel.className = 'lazy-load-sentinel';
        sentinel.style.height = '1px';
        container.appendChild(sentinel);

        observer.observe(sentinel);

        return {
            observer,
            sentinel,
            disconnect: () => {
                observer.disconnect();
                if (sentinel.parentNode) {
                    sentinel.parentNode.removeChild(sentinel);
                }
            }
        };
    }

    /**
     * Debounced search with caching
     */
    createDebouncedSearch(searchCallback, delay = 500) {
        let timeoutId;
        let lastQuery = '';
        const searchCache = new Map();

        return (query) => {
            clearTimeout(timeoutId);

            // Return cached result immediately if available
            if (searchCache.has(query)) {
                const cached = searchCache.get(query);
                if (Date.now() - cached.timestamp < 60000) { // 1 minute cache
                    searchCallback(cached.results);
                    return;
                }
            }

            timeoutId = setTimeout(async () => {
                if (query === lastQuery) return;
                lastQuery = query;

                try {
                    const results = await searchCallback(query);

                    // Cache results
                    searchCache.set(query, {
                        results,
                        timestamp: Date.now()
                    });

                    // Limit cache size
                    if (searchCache.size > 50) {
                        const firstKey = searchCache.keys().next().value;
                        searchCache.delete(firstKey);
                    }

                } catch (error) {
                    console.error('Search error:', error);
                }
            }, delay);
        };
    }

    /**
     * Memory usage monitoring
     */
    getMemoryUsage() {
        if ('memory' in performance) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    }

    /**
     * Performance monitoring
     */
    startPerformanceMonitoring() {
        setInterval(() => {
            const memory = this.getMemoryUsage();
            if (memory && memory.used > memory.limit * 0.8) {
                console.warn('⚠️ High memory usage detected, clearing cache');
                this.clearCache();
            }

            // Log cache statistics
            console.log(`📊 Cache: ${this.offlineCache.size} entries, Memory: ${memory ? memory.used + 'MB' : 'unknown'}`);
        }, 60000); // Check every minute
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

/**
 * Custom API Error class for better error handling
 */
class APIError extends Error {
    constructor(status, message) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.isPersianMessage = true; // Flag to indicate Persian error message
    }
}

// Create global API instance
window.legalAPI = new LegalDashboardAPI();
window.APIError = APIError;

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

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LegalDashboardAPI, APIError };
}

console.log('🔗 Legal Dashboard API Client loaded with enhanced error handling');
