/**
 * Scraping Control Panel for Legal Dashboard
 * Manages web scraping operations, real-time monitoring, and results display
 */

class ScrapingControlPanel {
    constructor() {
        this.baseEndpoint = '/api/scraping';
        this.currentJob = null;
        this.isRunning = false;
        this.statusInterval = null;
        this.logs = [];

        this.initializeEventListeners();
        this.loadScrapingStatus();
    }

    initializeEventListeners() {
        // Start scraping button
        const startBtn = document.getElementById('startScrapingBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startScraping());
        }

        // Stop scraping button
        const stopBtn = document.getElementById('stopScrapingBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopScraping());
        }

        // Refresh results button
        const refreshBtn = document.getElementById('refreshResultsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadScrapingResults());
        }

        // Clear logs button
        const clearLogsBtn = document.getElementById('clearLogsBtn');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => this.clearLogs());
        }
    }

    async startScraping() {
        if (this.isRunning) {
            this.showToast('اسکرپینگ در حال انجام است', 'warning');
            return;
        }

        const scrapingConfig = this.getScrapingConfig();
        if (!scrapingConfig.url) {
            this.showToast('لطفاً URL را وارد کنید', 'error');
            return;
        }

        try {
            this.isRunning = true;
            this.updateStartButton(true);
            this.addLog('شروع اسکرپینگ...', 'info');

            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/start`, {
                method: 'POST',
                body: JSON.stringify(scrapingConfig)
            });

            this.currentJob = response.job_id;
            this.showToast('اسکرپینگ شروع شد', 'success');
            this.addLog(`شغل اسکرپینگ ایجاد شد: ${this.currentJob}`, 'success');

            // Start monitoring
            this.startStatusMonitoring();
        } catch (error) {
            this.showToast(`خطا در شروع اسکرپینگ: ${error.message}`, 'error');
            this.addLog(`خطا در شروع اسکرپینگ: ${error.message}`, 'error');
            this.isRunning = false;
            this.updateStartButton(false);
        }
    }

    async stopScraping() {
        if (!this.isRunning) {
            this.showToast('هیچ اسکرپینگی در حال انجام نیست', 'warning');
            return;
        }

        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/stop`, {
                method: 'POST',
                body: JSON.stringify({ job_id: this.currentJob })
            });

            this.showToast('اسکرپینگ متوقف شد', 'success');
            this.addLog('اسکرپینگ متوقف شد', 'info');

            this.isRunning = false;
            this.currentJob = null;
            this.updateStartButton(false);
            this.stopStatusMonitoring();
        } catch (error) {
            this.showToast(`خطا در توقف اسکرپینگ: ${error.message}`, 'error');
            this.addLog(`خطا در توقف اسکرپینگ: ${error.message}`, 'error');
        }
    }

    async loadScrapingStatus() {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/status`);
            this.updateStatusDisplay(response);
        } catch (error) {
            console.error('Failed to load scraping status:', error);
        }
    }

    async loadScrapingResults() {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/results`);
            this.renderResults(response);
        } catch (error) {
            console.error('Failed to load scraping results:', error);
            this.showToast('خطا در بارگذاری نتایج', 'error');
        }
    }

    async loadScrapingStatistics() {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/statistics`);
            this.renderStatistics(response);
        } catch (error) {
            console.error('Failed to load scraping statistics:', error);
        }
    }

    startStatusMonitoring() {
        this.statusInterval = setInterval(async () => {
            if (this.isRunning) {
                await this.updateScrapingStatus();
            }
        }, 5000); // Update every 5 seconds
    }

    stopStatusMonitoring() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }

    async updateScrapingStatus() {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/status`);
            this.updateStatusDisplay(response);

            // Check if scraping is complete
            if (response.status === 'completed' || response.status === 'failed') {
                this.isRunning = false;
                this.currentJob = null;
                this.updateStartButton(false);
                this.stopStatusMonitoring();

                if (response.status === 'completed') {
                    this.addLog('اسکرپینگ تکمیل شد', 'success');
                    this.loadScrapingResults();
                } else {
                    this.addLog('اسکرپینگ با خطا مواجه شد', 'error');
                }
            }
        } catch (error) {
            console.error('Failed to update scraping status:', error);
        }
    }

    updateStatusDisplay(status) {
        const statusElement = document.getElementById('scrapingStatus');
        const progressElement = document.getElementById('scrapingProgress');
        const statsElement = document.getElementById('scrapingStats');

        if (statusElement) {
            statusElement.textContent = this.getStatusText(status.status);
            statusElement.className = `status-indicator ${this.getStatusClass(status.status)}`;
        }

        if (progressElement && status.progress) {
            progressElement.style.width = `${status.progress}%`;
            progressElement.textContent = `${status.progress}%`;
        }

        if (statsElement) {
            statsElement.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">صفحات پردازش شده:</span>
                    <span class="stat-value">${status.pages_processed || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">نتایج یافت شده:</span>
                    <span class="stat-value">${status.items_found || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">زمان سپری شده:</span>
                    <span class="stat-value">${status.elapsed_time || '0s'}</span>
                </div>
            `;
        }
    }

    renderResults(results) {
        const container = document.getElementById('scrapingResults');
        if (!container) return;

        if (!results.items || results.items.length === 0) {
            container.innerHTML = '<p class="no-results">هیچ نتیجه‌ای یافت نشد</p>';
            return;
        }

        const resultsHTML = results.items.map(item => `
            <div class="scraping-item">
                <div class="item-header">
                    <h4 class="item-title">${item.title || 'بدون عنوان'}</h4>
                    <span class="item-rating">امتیاز: ${item.rating || 0}</span>
                </div>
                <div class="item-content">
                    <p class="item-url">
                        <a href="${item.url}" target="_blank">${item.url}</a>
                    </p>
                    <p class="item-description">${item.description || 'توضیحات موجود نیست'}</p>
                    <div class="item-meta">
                        <span class="item-date">${this.formatDate(item.date)}</span>
                        <span class="item-category">${item.category || 'نامشخص'}</span>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = resultsHTML;
    }

    renderStatistics(stats) {
        const container = document.getElementById('scrapingStatistics');
        if (!container) return;

        const statsHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">${stats.total_scraped || 0}</div>
                    <div class="stat-label">کل نتایج</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.success_rate || 0}%</div>
                    <div class="stat-label">نرخ موفقیت</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.average_speed || 0}</div>
                    <div class="stat-label">سرعت متوسط (صفحه/دقیقه)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.average_rating || 0}</div>
                    <div class="stat-label">امتیاز متوسط</div>
                </div>
            </div>
        `;

        container.innerHTML = statsHTML;
    }

    getScrapingConfig() {
        const urlInput = document.getElementById('scrapingUrl');
        const depthInput = document.getElementById('scrapingDepth');
        const maxPagesInput = document.getElementById('maxPages');
        const filtersInput = document.getElementById('scrapingFilters');

        return {
            url: urlInput ? urlInput.value : '',
            depth: depthInput ? parseInt(depthInput.value) : 1,
            max_pages: maxPagesInput ? parseInt(maxPagesInput.value) : 100,
            filters: filtersInput ? filtersInput.value : ''
        };
    }

    updateStartButton(isRunning) {
        const startBtn = document.getElementById('startScrapingBtn');
        const stopBtn = document.getElementById('stopScrapingBtn');

        if (startBtn) {
            startBtn.disabled = isRunning;
            startBtn.textContent = isRunning ? 'در حال اجرا...' : 'شروع اسکرپینگ';
        }

        if (stopBtn) {
            stopBtn.disabled = !isRunning;
            stopBtn.style.display = isRunning ? 'inline-block' : 'none';
        }
    }

    addLog(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString('fa-IR');
        const logEntry = {
            timestamp,
            message,
            type
        };

        this.logs.unshift(logEntry);
        this.renderLogs();

        // Keep only last 100 logs
        if (this.logs.length > 100) {
            this.logs = this.logs.slice(0, 100);
        }
    }

    renderLogs() {
        const container = document.getElementById('scrapingLogs');
        if (!container) return;

        const logsHTML = this.logs.map(log => `
            <div class="log-entry ${log.type}">
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('');

        container.innerHTML = logsHTML;
    }

    clearLogs() {
        this.logs = [];
        this.renderLogs();
        this.showToast('لاگ‌ها پاک شدند', 'info');
    }

    getStatusClass(status) {
        const statusMap = {
            'idle': 'status-idle',
            'running': 'status-running',
            'completed': 'status-completed',
            'failed': 'status-failed',
            'stopped': 'status-stopped'
        };
        return statusMap[status] || 'status-unknown';
    }

    getStatusText(status) {
        const statusMap = {
            'idle': 'آماده',
            'running': 'در حال اجرا',
            'completed': 'تکمیل شده',
            'failed': 'ناموفق',
            'stopped': 'متوقف شده'
        };
        return statusMap[status] || 'نامشخص';
    }

    formatDate(dateString) {
        if (!dateString) return 'نامشخص';
        const date = new Date(dateString);
        return date.toLocaleDateString('fa-IR');
    }

    showToast(message, type = 'info') {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize scraping control panel
const scrapingControlPanel = new ScrapingControlPanel(); 