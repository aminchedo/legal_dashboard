/**
 * Legal Dashboard Core Module
 * ==========================
 * 
 * Shared core functionality for cross-page communication and data synchronization.
 * This module provides event-driven updates and shared state management across all pages.
 */

class DashboardCore {
    constructor() {
        this.eventBus = new EventTarget();
        this.cache = new Map();
        this.apiClient = null;
        this.isInitialized = false;

        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    /**
     * Initialize the core module
     */
    initialize() {
        if (this.isInitialized) return;

        console.log('🚀 Initializing Dashboard Core...');

        // Initialize API client
        this.apiClient = new LegalDashboardAPI();

        // Set up localStorage synchronization
        this.setupLocalStorageSync();

        // Set up periodic health checks
        this.setupHealthChecks();

        // Set up cross-page event listeners
        this.setupEventListeners();

        this.isInitialized = true;
        console.log('✅ Dashboard Core initialized');

        // Broadcast initialization event
        this.broadcast('coreInitialized', { timestamp: Date.now() });
    }

    /**
     * Broadcast events across pages
     */
    broadcast(eventName, data = {}) {
        const event = new CustomEvent(eventName, {
            detail: {
                ...data,
                timestamp: Date.now(),
                source: window.location.pathname
            }
        });

        this.eventBus.dispatchEvent(event);

        // Also store in localStorage for cross-tab communication
        this.storeEvent(eventName, data);

        console.log(`📡 Broadcast: ${eventName}`, data);
    }

    /**
     * Listen for cross-page events
     */
    listen(eventName, callback) {
        const wrappedCallback = (event) => {
            callback(event.detail);
        };

        this.eventBus.addEventListener(eventName, wrappedCallback);

        // Return unsubscribe function
        return () => {
            this.eventBus.removeEventListener(eventName, wrappedCallback);
        };
    }

    /**
     * Store event in localStorage for cross-tab communication
     */
    storeEvent(eventName, data) {
        try {
            const events = JSON.parse(localStorage.getItem('dashboard_events') || '[]');
            events.push({
                name: eventName,
                data: data,
                timestamp: Date.now(),
                source: window.location.pathname
            });

            // Keep only last 50 events
            if (events.length > 50) {
                events.splice(0, events.length - 50);
            }

            localStorage.setItem('dashboard_events', JSON.stringify(events));
        } catch (error) {
            console.warn('Failed to store event in localStorage:', error);
        }
    }

    /**
     * Setup localStorage synchronization
     */
    setupLocalStorageSync() {
        // Listen for storage changes (cross-tab communication)
        window.addEventListener('storage', (event) => {
            if (event.key === 'dashboard_events') {
                try {
                    const events = JSON.parse(event.newValue || '[]');
                    const latestEvent = events[events.length - 1];

                    if (latestEvent && latestEvent.source !== window.location.pathname) {
                        // Re-broadcast event from other tab
                        this.eventBus.dispatchEvent(new CustomEvent(latestEvent.name, {
                            detail: latestEvent.data
                        }));
                    }
                } catch (error) {
                    console.warn('Failed to process storage event:', error);
                }
            }
        });
    }

    /**
     * Setup periodic health checks
     */
    setupHealthChecks() {
        // Check API health every 30 seconds
        setInterval(async () => {
            try {
                const health = await this.apiClient.healthCheck();
                this.broadcast('healthUpdate', health);
            } catch (error) {
                this.broadcast('healthUpdate', { status: 'unhealthy', error: error.message });
            }
        }, 30000);
    }

    /**
     * Setup common event listeners
     */
    setupEventListeners() {
        // Listen for document uploads
        this.listen('documentUploaded', (data) => {
            this.handleDocumentUpload(data);
        });

        // Listen for document updates
        this.listen('documentUpdated', (data) => {
            this.handleDocumentUpdate(data);
        });

        // Listen for document deletions
        this.listen('documentDeleted', (data) => {
            this.handleDocumentDelete(data);
        });

        // Listen for scraping updates
        this.listen('scrapingUpdate', (data) => {
            this.handleScrapingUpdate(data);
        });

        // Listen for system health updates
        this.listen('healthUpdate', (data) => {
            this.handleHealthUpdate(data);
        });
    }

    /**
     * Handle document upload events
     */
    handleDocumentUpload(data) {
        console.log('📄 Document uploaded:', data);

        // Update cache
        this.cache.set(`document_${data.fileId}`, data);

        // Refresh document lists on relevant pages
        if (window.location.pathname.includes('documents.html') ||
            window.location.pathname.includes('improved_legal_dashboard.html')) {
            this.refreshDocumentList();
        }

        // Update dashboard stats
        this.updateDashboardStats();

        // Show notification
        showToast(`فایل "${data.fileName}" با موفقیت آپلود شد`, 'success');
    }

    /**
     * Handle document update events
     */
    handleDocumentUpdate(data) {
        console.log('📝 Document updated:', data);

        // Update cache
        this.cache.set(`document_${data.documentId}`, data);

        // Refresh document lists
        this.refreshDocumentList();

        // Show notification
        showToast('سند با موفقیت به‌روزرسانی شد', 'success');
    }

    /**
     * Handle document delete events
     */
    handleDocumentDelete(data) {
        console.log('🗑️ Document deleted:', data);

        // Remove from cache
        this.cache.delete(`document_${data.documentId}`);

        // Refresh document lists
        this.refreshDocumentList();

        // Update dashboard stats
        this.updateDashboardStats();

        // Show notification
        showToast('سند با موفقیت حذف شد', 'info');
    }

    /**
     * Handle scraping update events
     */
    handleScrapingUpdate(data) {
        console.log('🕷️ Scraping update:', data);

        // Update scraping dashboard if on that page
        if (window.location.pathname.includes('scraping_dashboard.html')) {
            this.refreshScrapingDashboard();
        }

        // Show notification
        showToast(`وضعیت scraping: ${data.status}`, 'info');
    }

    /**
     * Handle health update events
     */
    handleHealthUpdate(data) {
        console.log('💓 Health update:', data);

        // Update health indicators on all pages
        this.updateHealthIndicators(data);
    }

    /**
     * Refresh document list (if function exists)
     */
    refreshDocumentList() {
        if (typeof loadDocuments === 'function') {
            loadDocuments();
        }

        if (typeof refreshDocumentTable === 'function') {
            refreshDocumentTable();
        }
    }

    /**
     * Update dashboard statistics
     */
    async updateDashboardStats() {
        try {
            const summary = await this.apiClient.getDashboardSummary();
            this.broadcast('dashboardStatsUpdated', summary);

            // Update dashboard if on dashboard page
            if (window.location.pathname.includes('improved_legal_dashboard.html')) {
                if (typeof updateDashboardStats === 'function') {
                    updateDashboardStats(summary);
                }
            }
        } catch (error) {
            console.error('Failed to update dashboard stats:', error);
        }
    }

    /**
     * Refresh scraping dashboard
     */
    refreshScrapingDashboard() {
        if (typeof loadScrapingData === 'function') {
            loadScrapingData();
        }

        if (typeof updateScrapingStatus === 'function') {
            updateScrapingStatus();
        }
    }

    /**
     * Update health indicators
     */
    updateHealthIndicators(healthData) {
        const healthElements = document.querySelectorAll('.health-indicator');

        healthElements.forEach(element => {
            const status = healthData.status || 'unknown';
            element.className = `health-indicator ${status}`;
            element.textContent = status === 'healthy' ? '🟢' : '🔴';
        });
    }

    /**
     * Get cached data
     */
    getCachedData(key) {
        return this.cache.get(key);
    }

    /**
     * Set cached data
     */
    setCachedData(key, data) {
        this.cache.set(key, data);
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Get API client
     */
    getApiClient() {
        return this.apiClient;
    }

    /**
     * Force refresh all data
     */
    async forceRefresh() {
        console.log('🔄 Force refreshing all data...');

        try {
            // Clear cache
            this.clearCache();

            // Refresh document list
            this.refreshDocumentList();

            // Update dashboard stats
            await this.updateDashboardStats();

            // Refresh scraping data
            this.refreshScrapingDashboard();

            this.broadcast('dataRefreshed', { timestamp: Date.now() });

            showToast('داده‌ها با موفقیت به‌روزرسانی شدند', 'success');
        } catch (error) {
            console.error('Failed to force refresh:', error);
            showToast('خطا در به‌روزرسانی داده‌ها', 'error');
        }
    }

    /**
     * Enhanced error handling with retry mechanism
     */
    async retryOperation(operation, maxRetries = 3, delay = 1000) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                console.warn(`Operation failed (attempt ${attempt}/${maxRetries}):`, error);

                if (attempt === maxRetries) {
                    throw error;
                }

                // Wait before retrying (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, delay * attempt));
            }
        }
    }

    /**
     * Check if system is online
     */
    async isOnline() {
        try {
            const response = await fetch('/api/health', {
                method: 'HEAD',
                timeout: 5000
            });
            return response.ok;
        } catch {
            return false;
        }
    }

    /**
     * Enhanced notification system with Persian messages
     */
    showPersianToast(messageKey, type = 'info', duration = 3000) {
        const messages = {
            'upload_success': 'فایل با موفقیت آپلود شد',
            'upload_error': 'خطا در آپلود فایل',
            'delete_success': 'حذف با موفقیت انجام شد',
            'delete_error': 'خطا در حذف',
            'update_success': 'به‌روزرسانی با موفقیت انجام شد',
            'update_error': 'خطا در به‌روزرسانی',
            'network_error': 'خطا در اتصال به شبکه',
            'server_error': 'خطای سرور',
            'loading': 'در حال بارگذاری...',
            'processing': 'در حال پردازش...',
            'completed': 'عملیات تکمیل شد',
            'cancelled': 'عملیات لغو شد'
        };

        const message = messages[messageKey] || messageKey;

        if (typeof showToast === 'function') {
            showToast(message, type, duration);
        } else {
            console.log(`Toast: ${message} (${type})`);
        }
    }

    /**
     * Local storage wrapper with error handling
     */
    setLocalStorage(key, value, expiry = null) {
        try {
            const item = {
                value: value,
                timestamp: Date.now(),
                expiry: expiry
            };
            localStorage.setItem(`dashboard_${key}`, JSON.stringify(item));
            return true;
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
            return false;
        }
    }

    getLocalStorage(key) {
        try {
            const item = JSON.parse(localStorage.getItem(`dashboard_${key}`));
            if (!item) return null;

            // Check expiry
            if (item.expiry && Date.now() > item.expiry) {
                localStorage.removeItem(`dashboard_${key}`);
                return null;
            }

            return item.value;
        } catch (error) {
            console.warn('Failed to read from localStorage:', error);
            return null;
        }
    }

    /**
     * Debounce function for search and API calls
     */
    debounce(func, wait) {
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

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// Global instance
const dashboardCore = new DashboardCore();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardCore;
}

// Make available globally
window.dashboardCore = dashboardCore;

console.log('📦 Dashboard Core module loaded'); 