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