/**
 * Search Engine for Legal Dashboard
 * ================================
 * 
 * Handles advanced search functionality, filters, suggestions, result highlighting,
 * search analytics, and export options for legal documents.
 */

class SearchEngine {
    constructor() {
        this.searchHistory = [];
        this.searchSuggestions = [];
        this.currentSearch = '';
        this.searchFilters = {
            dateRange: null,
            documentType: 'all',
            status: 'all',
            tags: [],
            size: null,
            author: '',
            content: ''
        };
        this.searchResults = [];
        this.isSearching = false;
        this.apiClient = null;
        this.eventBus = null;
        this.debounceTimer = null;

        this.init();
    }

    /**
     * Initialize search engine
     */
    init() {
        this.apiClient = window.LegalDashboardAPI || new LegalDashboardAPI();
        this.eventBus = window.dashboardCore?.eventBus || new EventTarget();
        
        this.loadSearchHistory();
        this.setupEventListeners();
        this.setupSearchSuggestions();
        
        console.log('🔍 Search Engine initialized');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search input
        document.addEventListener('input', (e) => {
            if (e.target.matches('[data-search-input]')) {
                this.handleSearchInput(e.target);
            }
        });

        // Search form submission
        document.addEventListener('submit', (e) => {
            if (e.target.matches('[data-search-form]')) {
                e.preventDefault();
                this.performSearch();
            }
        });

        // Filter changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-search-filter]')) {
                this.handleFilterChange(e.target);
            }
        });

        // Search suggestions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-search-suggestion]')) {
                e.preventDefault();
                this.selectSuggestion(e.target.textContent);
            }
        });

        // Export search results
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-export-results]')) {
                e.preventDefault();
                this.exportSearchResults();
            }
        });

        // Advanced search toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-advanced-search-toggle]')) {
                e.preventDefault();
                this.toggleAdvancedSearch();
            }
        });

        // Clear search
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-clear-search]')) {
                e.preventDefault();
                this.clearSearch();
            }
        });
    }

    /**
     * Handle search input
     */
    handleSearchInput(input) {
        const query = input.value.trim();
        this.currentSearch = query;

        // Clear previous debounce timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Debounce search suggestions
        this.debounceTimer = setTimeout(() => {
            if (query.length >= 2) {
                this.loadSearchSuggestions(query);
            } else {
                this.hideSearchSuggestions();
            }
        }, 300);

        // Auto-search if query is long enough
        if (query.length >= 3) {
            this.performSearch();
        }
    }

    /**
     * Load search suggestions
     */
    async loadSearchSuggestions(query) {
        try {
            const response = await this.apiClient.getSearchSuggestions(query);
            
            if (response.success) {
                this.searchSuggestions = response.data.suggestions;
                this.showSearchSuggestions();
            }
        } catch (error) {
            console.error('Error loading search suggestions:', error);
        }
    }

    /**
     * Show search suggestions
     */
    showSearchSuggestions() {
        const container = document.querySelector('.search-suggestions');
        if (!container) return;

        if (this.searchSuggestions.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = this.searchSuggestions.map(suggestion => `
            <div class="suggestion-item" data-search-suggestion>
                <i class="fas fa-search"></i>
                <span>${this.highlightQuery(suggestion, this.currentSearch)}</span>
            </div>
        `).join('');

        container.style.display = 'block';
    }

    /**
     * Hide search suggestions
     */
    hideSearchSuggestions() {
        const container = document.querySelector('.search-suggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    /**
     * Highlight query in suggestion
     */
    highlightQuery(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Select search suggestion
     */
    selectSuggestion(suggestion) {
        const searchInput = document.querySelector('[data-search-input]');
        if (searchInput) {
            searchInput.value = suggestion;
            this.currentSearch = suggestion;
            this.hideSearchSuggestions();
            this.performSearch();
        }
    }

    /**
     * Setup search suggestions
     */
    setupSearchSuggestions() {
        // Create suggestions container if it doesn't exist
        if (!document.querySelector('.search-suggestions')) {
            const container = document.createElement('div');
            container.className = 'search-suggestions';
            container.style.display = 'none';
            
            const searchContainer = document.querySelector('.search-container');
            if (searchContainer) {
                searchContainer.appendChild(container);
            }
        }
    }

    /**
     * Perform search
     */
    async performSearch() {
        if (this.isSearching) return;

        this.isSearching = true;
        this.showSearchLoading();

        try {
            const searchParams = {
                query: this.currentSearch,
                filters: this.searchFilters,
                page: 1,
                limit: 20
            };

            const response = await this.apiClient.searchDocuments(searchParams);
            
            if (response.success) {
                this.searchResults = response.data.results;
                this.renderSearchResults();
                this.updateSearchHistory();
                this.updateSearchAnalytics();
            } else {
                this.showSearchError(response.message);
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError('خطا در جستجو');
        } finally {
            this.isSearching = false;
            this.hideSearchLoading();
        }
    }

    /**
     * Show search loading
     */
    showSearchLoading() {
        const container = document.querySelector('.search-results');
        if (container) {
            container.innerHTML = `
                <div class="search-loading">
                    <div class="loading-spinner"></div>
                    <p>در حال جستجو...</p>
                </div>
            `;
        }
    }

    /**
     * Hide search loading
     */
    hideSearchLoading() {
        const loading = document.querySelector('.search-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Show search error
     */
    showSearchError(message) {
        const container = document.querySelector('.search-results');
        if (container) {
            container.innerHTML = `
                <div class="search-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    /**
     * Render search results
     */
    renderSearchResults() {
        const container = document.querySelector('.search-results');
        if (!container) return;

        if (this.searchResults.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>نتیجه‌ای یافت نشد</h3>
                    <p>لطفاً کلمات کلیدی یا فیلترهای دیگری را امتحان کنید</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="search-results-header">
                <h3>نتایج جستجو (${this.searchResults.length})</h3>
                <div class="search-actions">
                    <button class="btn btn-secondary" data-export-results>
                        <i class="fas fa-download"></i>
                        خروجی
                    </button>
                </div>
            </div>
            <div class="search-results-list">
                ${this.searchResults.map(result => this.renderSearchResult(result)).join('')}
            </div>
        `;
    }

    /**
     * Render search result
     */
    renderSearchResult(result) {
        const relevance = result.relevance || 0;
        const relevanceClass = relevance > 80 ? 'high-relevance' : relevance > 60 ? 'medium-relevance' : 'low-relevance';

        return `
            <div class="search-result ${relevanceClass}" data-result-id="${result.id}">
                <div class="result-header">
                    <div class="result-icon">
                        <i class="${this.getFileIcon(result.type)}"></i>
                    </div>
                    <div class="result-info">
                        <h4 class="result-title">
                            <a href="#" onclick="searchEngine.openResult('${result.id}')">
                                ${this.highlightQuery(result.name, this.currentSearch)}
                            </a>
                        </h4>
                        <div class="result-meta">
                            <span class="result-type">${result.type}</span>
                            <span class="result-size">${this.formatFileSize(result.size)}</span>
                            <span class="result-date">${this.formatDate(result.created_at)}</span>
                            <span class="result-relevance">${relevance}% مرتبط</span>
                        </div>
                    </div>
                    <div class="result-actions">
                        <button class="btn-icon" onclick="searchEngine.previewResult('${result.id}')" title="پیش‌نمایش">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" onclick="searchEngine.downloadResult('${result.id}')" title="دانلود">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
                ${result.excerpt ? `
                    <div class="result-excerpt">
                        ${this.highlightQuery(result.excerpt, this.currentSearch)}
                    </div>
                ` : ''}
                ${result.tags && result.tags.length > 0 ? `
                    <div class="result-tags">
                        ${result.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get file icon
     */
    getFileIcon(fileType) {
        const icons = {
            'application/pdf': 'fas fa-file-pdf',
            'application/msword': 'fas fa-file-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fas fa-file-word',
            'text/plain': 'fas fa-file-alt',
            'image/jpeg': 'fas fa-file-image',
            'image/png': 'fas fa-file-image',
            'image/gif': 'fas fa-file-image'
        };
        
        return icons[fileType] || 'fas fa-file';
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fa-IR');
    }

    /**
     * Handle filter change
     */
    handleFilterChange(target) {
        const filterType = target.getAttribute('data-search-filter');
        const value = target.value;

        switch (filterType) {
            case 'dateRange':
                this.searchFilters.dateRange = value;
                break;
            case 'documentType':
                this.searchFilters.documentType = value;
                break;
            case 'status':
                this.searchFilters.status = value;
                break;
            case 'size':
                this.searchFilters.size = value;
                break;
            case 'author':
                this.searchFilters.author = value;
                break;
        }

        // Perform search with new filters
        this.performSearch();
    }

    /**
     * Toggle advanced search
     */
    toggleAdvancedSearch() {
        const advancedPanel = document.querySelector('.advanced-search-panel');
        if (advancedPanel) {
            advancedPanel.classList.toggle('expanded');
        }
    }

    /**
     * Clear search
     */
    clearSearch() {
        this.currentSearch = '';
        this.searchResults = [];
        
        const searchInput = document.querySelector('[data-search-input]');
        if (searchInput) {
            searchInput.value = '';
        }

        // Clear filters
        this.searchFilters = {
            dateRange: null,
            documentType: 'all',
            status: 'all',
            tags: [],
            size: null,
            author: '',
            content: ''
        };

        // Reset filter inputs
        document.querySelectorAll('[data-search-filter]').forEach(input => {
            input.value = '';
        });

        // Hide results
        const resultsContainer = document.querySelector('.search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }

        this.hideSearchSuggestions();
    }

    /**
     * Open search result
     */
    openResult(resultId) {
        // Navigate to document page or open in modal
        window.location.href = `/documents.html?id=${resultId}`;
    }

    /**
     * Preview search result
     */
    async previewResult(resultId) {
        try {
            const result = this.searchResults.find(r => r.id === resultId);
            if (!result) return;

            const response = await this.apiClient.getDocument(resultId);
            
            if (response.success) {
                this.showResultPreview(response.data);
            } else {
                this.showError('خطا در پیش‌نمایش', response.message);
            }
        } catch (error) {
            this.showError('خطا در پیش‌نمایش', error.message);
        }
    }

    /**
     * Show result preview
     */
    showResultPreview(document) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${document.name}</h3>
                    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="document-preview">
                        ${this.renderDocumentPreview(document)}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    /**
     * Render document preview
     */
    renderDocumentPreview(document) {
        if (document.type.startsWith('image/')) {
            return `<img src="${document.previewUrl}" alt="${document.name}" class="preview-image">`;
        } else if (document.type === 'application/pdf') {
            return `<iframe src="${document.previewUrl}" class="preview-pdf"></iframe>`;
        } else {
            return `
                <div class="preview-text">
                    <pre>${document.content || 'محتوای فایل در دسترس نیست'}</pre>
                </div>
            `;
        }
    }

    /**
     * Download search result
     */
    async downloadResult(resultId) {
        try {
            const result = this.searchResults.find(r => r.id === resultId);
            if (!result) return;

            const response = await this.apiClient.downloadDocument(resultId);
            
            if (response.success) {
                const link = document.createElement('a');
                link.href = response.data.downloadUrl;
                link.download = result.name;
                link.click();
                
                this.showSuccess('دانلود موفق', 'فایل با موفقیت دانلود شد');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            this.showError('خطا در دانلود', error.message);
        }
    }

    /**
     * Export search results
     */
    async exportSearchResults() {
        if (this.searchResults.length === 0) {
            this.showError('خطا', 'نتیجه‌ای برای خروجی وجود ندارد');
            return;
        }

        try {
            const exportFormat = prompt('فرمت خروجی را انتخاب کنید (pdf/excel):', 'pdf');
            
            if (!exportFormat) return;

            const response = await this.apiClient.exportSearchResults({
                results: this.searchResults,
                format: exportFormat,
                query: this.currentSearch,
                filters: this.searchFilters
            });

            if (response.success) {
                const link = document.createElement('a');
                link.href = response.data.downloadUrl;
                link.download = `search_results.${exportFormat}`;
                link.click();
                
                this.showSuccess('خروجی موفق', 'نتایج جستجو با موفقیت خروجی گرفته شد');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            this.showError('خطا در خروجی', error.message);
        }
    }

    /**
     * Update search history
     */
    updateSearchHistory() {
        if (this.currentSearch.trim()) {
            // Add to history if not already present
            if (!this.searchHistory.includes(this.currentSearch)) {
                this.searchHistory.unshift(this.currentSearch);
                
                // Keep only last 10 searches
                if (this.searchHistory.length > 10) {
                    this.searchHistory = this.searchHistory.slice(0, 10);
                }
                
                this.saveSearchHistory();
            }
        }
    }

    /**
     * Load search history
     */
    loadSearchHistory() {
        try {
            const history = localStorage.getItem('search_history');
            if (history) {
                this.searchHistory = JSON.parse(history);
            }
        } catch (error) {
            console.error('Error loading search history:', error);
        }
    }

    /**
     * Save search history
     */
    saveSearchHistory() {
        try {
            localStorage.setItem('search_history', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    }

    /**
     * Update search analytics
     */
    updateSearchAnalytics() {
        const analytics = {
            query: this.currentSearch,
            results: this.searchResults.length,
            filters: this.searchFilters,
            timestamp: Date.now()
        };

        // Send analytics to server
        this.apiClient.trackSearchAnalytics(analytics).catch(error => {
            console.error('Error tracking search analytics:', error);
        });
    }

    /**
     * Get search statistics
     */
    getSearchStats() {
        return {
            totalSearches: this.searchHistory.length,
            currentResults: this.searchResults.length,
            averageResults: this.calculateAverageResults()
        };
    }

    /**
     * Calculate average results
     */
    calculateAverageResults() {
        // This would be calculated from historical data
        return this.searchResults.length;
    }

    /**
     * Show success notification
     */
    showSuccess(title, message) {
        if (window.notificationManager) {
            window.notificationManager.showSuccess(title, message);
        } else {
            alert(`${title}: ${message}`);
        }
    }

    /**
     * Show error notification
     */
    showError(title, message) {
        if (window.notificationManager) {
            window.notificationManager.showError(title, message);
        } else {
            alert(`${title}: ${message}`);
        }
    }
}

// Initialize search engine
const searchEngine = new SearchEngine();

// Export for use in other modules
window.SearchEngine = SearchEngine;
window.searchEngine = searchEngine;