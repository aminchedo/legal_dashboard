/**
 * Legal Dashboard API Client
 * =========================
 * * Updated to use ES module exports for robust dependency management.
 */

export class LegalDashboardAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
        this.apiBase = `${this.baseUrl}/api`;
        this.defaultHeaders = { 'Content-Type': 'application/json' };
    }

    async request(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const config = { ...options, headers: { ...this.defaultHeaders, ...options.headers } };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            const contentType = response.headers.get('content-type');
            return contentType?.includes('application/json') ? response.json() : response.text();
        } catch (error) {
            console.error(`API Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // --- Existing Methods ---
    async healthCheck() { return this.request('/health'); }
    async getDashboardSummary() { return this.request('/dashboard/summary'); }
    async getDocuments(params = {}) {
        const searchParams = new URLSearchParams(params);
        return this.request(`/documents?${searchParams.toString()}`);
    }
    // ... other methods

    // --- SOURCE MANAGEMENT METHODS ---
    async getAllSources() {
        return this.request('/sources/');
    }

    async updateSource(sourceId, data) {
        return this.request(`/sources/${sourceId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // --- DISCOVERY METHOD ---
    async discoverSources(topic) {
        return this.request('/scraping/discover', {
            method: 'POST',
            body: JSON.stringify({ topic: topic })
        });
    }
}

// Create and export a single, global instance of the API client
export const legalAPI = new LegalDashboardAPI();

// Test connection on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await legalAPI.healthCheck();
        console.log('✅ Backend connection successful');
    } catch (error) {
        console.warn('⚠️ Backend connection failed:', error.message);
        // Assuming a global notification function exists
        if (window.notifications) {
            window.notifications.showWarning('اتصال به سرور برقرار نشد', 'حالت آفلاین فعال است.');
        }
    }
});
