/**
 * Legal Dashboard API Client
 * =========================
 * * Updated with methods for source management and discovery.
 */

class LegalDashboardAPI {
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
    // ... (all your other existing methods like getDashboardSummary, getDocuments, etc.)

    // --- NEW SOURCE MANAGEMENT METHODS ---

    /**
     * Gets all sources from the database.
     * @returns {Promise<Array>} A list of source objects.
     */
    async getAllSources() {
        return this.request('/sources/');
    }

    /**
     * Updates a source's credibility and status.
     * @param {number} sourceId The ID of the source to update.
     * @param {object} data The update data { credibility_score, status }.
     * @returns {Promise<Object>} The success message.
     */
    async updateSource(sourceId, data) {
        return this.request(`/sources/${sourceId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // --- NEW DISCOVERY METHOD ---

    /**
     * Discovers new sources and keywords for a topic using Gemini.
     * @param {string} topic The legal topic to research.
     * @returns {Promise<Object>} An object with suggested_keywords and suggested_sources.
     */
    async discoverSources(topic) {
        return this.request('/scraping/discover', {
            method: 'POST',
            body: JSON.stringify({ topic: topic })
        });
    }
}

// Global API instance
window.legalAPI = new LegalDashboardAPI();
