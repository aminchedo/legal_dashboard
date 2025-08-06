/**
 * Chart Manager for Legal Dashboard
 * ================================
 * 
 * Handles data visualization, chart creation, real-time updates,
 * and interactive analytics for legal documents and system metrics.
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.chartConfigs = {};
        this.dataCache = new Map();
        this.updateIntervals = new Map();
        this.apiClient = null;
        this.eventBus = null;

        this.init();
    }

    /**
     * Initialize chart manager
     */
    init() {
        this.apiClient = window.LegalDashboardAPI || new LegalDashboardAPI();
        this.eventBus = window.dashboardCore?.eventBus || new EventTarget();
        
        this.setupChartConfigs();
        this.setupEventListeners();
        this.initializeCharts();
        
        console.log('📊 Chart Manager initialized');
    }

    /**
     * Setup chart configurations
     */
    setupChartConfigs() {
        this.chartConfigs = {
            documentTrends: {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'روند اسناد',
                            font: {
                                family: 'Vazirmatn',
                                size: 16
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'تاریخ',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'تعداد اسناد',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        }
                    }
                }
            },
            documentTypes: {
                type: 'doughnut',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'انواع اسناد',
                            font: {
                                family: 'Vazirmatn',
                                size: 16
                            }
                        }
                    }
                }
            },
            processingStatus: {
                type: 'bar',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'وضعیت پردازش',
                            font: {
                                family: 'Vazirmatn',
                                size: 16
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'وضعیت',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'تعداد',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        }
                    }
                }
            },
            systemPerformance: {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'عملکرد سیستم',
                            font: {
                                family: 'Vazirmatn',
                                size: 16
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'زمان',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'درصد',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        }
                    }
                }
            },
            uploadActivity: {
                type: 'area',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'فعالیت آپلود',
                            font: {
                                family: 'Vazirmatn',
                                size: 16
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'ساعت',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'تعداد فایل',
                                font: {
                                    family: 'Vazirmatn'
                                }
                            }
                        }
                    }
                }
            }
        };
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for data updates
        this.eventBus?.addEventListener('data:updated', (e) => {
            this.handleDataUpdate(e.detail);
        });

        // Listen for chart refresh requests
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-refresh-chart]')) {
                e.preventDefault();
                const chartId = e.target.getAttribute('data-chart-id');
                this.refreshChart(chartId);
            }
        });

        // Listen for chart export requests
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-export-chart]')) {
                e.preventDefault();
                const chartId = e.target.getAttribute('data-chart-id');
                this.exportChart(chartId);
            }
        });

        // Listen for chart type changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-chart-type]')) {
                e.preventDefault();
                const chartId = e.target.getAttribute('data-chart-id');
                const newType = e.target.value;
                this.changeChartType(chartId, newType);
            }
        });
    }

    /**
     * Initialize charts
     */
    initializeCharts() {
        // Initialize document trends chart
        this.createChart('documentTrends', 'document-trends-chart');
        
        // Initialize document types chart
        this.createChart('documentTypes', 'document-types-chart');
        
        // Initialize processing status chart
        this.createChart('processingStatus', 'processing-status-chart');
        
        // Initialize system performance chart
        this.createChart('systemPerformance', 'system-performance-chart');
        
        // Initialize upload activity chart
        this.createChart('uploadActivity', 'upload-activity-chart');

        // Start real-time updates
        this.startRealTimeUpdates();
    }

    /**
     * Create chart
     */
    createChart(chartType, canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`Canvas with id '${canvasId}' not found`);
            return;
        }

        const ctx = canvas.getContext('2d');
        const config = this.chartConfigs[chartType];
        
        if (!config) {
            console.warn(`Chart config for '${chartType}' not found`);
            return;
        }

        const chart = new Chart(ctx, {
            type: config.type,
            data: {
                labels: [],
                datasets: []
            },
            options: config.options
        });

        this.charts.set(chartType, chart);
        
        // Load initial data
        this.loadChartData(chartType);
        
        console.log(`📊 Created chart: ${chartType}`);
    }

    /**
     * Load chart data
     */
    async loadChartData(chartType) {
        try {
            let data;
            
            switch (chartType) {
                case 'documentTrends':
                    data = await this.loadDocumentTrendsData();
                    break;
                case 'documentTypes':
                    data = await this.loadDocumentTypesData();
                    break;
                case 'processingStatus':
                    data = await this.loadProcessingStatusData();
                    break;
                case 'systemPerformance':
                    data = await this.loadSystemPerformanceData();
                    break;
                case 'uploadActivity':
                    data = await this.loadUploadActivityData();
                    break;
                default:
                    console.warn(`Unknown chart type: ${chartType}`);
                    return;
            }

            this.updateChart(chartType, data);
            this.dataCache.set(chartType, data);
            
        } catch (error) {
            console.error(`Error loading data for chart ${chartType}:`, error);
            this.showChartError(chartType, error.message);
        }
    }

    /**
     * Load document trends data
     */
    async loadDocumentTrendsData() {
        const response = await this.apiClient.getProcessingTrends('weekly');
        
        if (response.success) {
            return {
                labels: response.data.labels,
                datasets: [{
                    label: 'اسناد جدید',
                    data: response.data.values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            };
        }
        
        throw new Error(response.message);
    }

    /**
     * Load document types data
     */
    async loadDocumentTypesData() {
        const response = await this.apiClient.getCategoryDistribution();
        
        if (response.success) {
            const colors = [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
            ];

            return {
                labels: response.data.labels,
                datasets: [{
                    data: response.data.values,
                    backgroundColor: colors.slice(0, response.data.values.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            };
        }
        
        throw new Error(response.message);
    }

    /**
     * Load processing status data
     */
    async loadProcessingStatusData() {
        const response = await this.apiClient.getStatusDistribution();
        
        if (response.success) {
            return {
                labels: response.data.labels,
                datasets: [{
                    label: 'تعداد اسناد',
                    data: response.data.values,
                    backgroundColor: [
                        '#10b981', // Completed
                        '#f59e0b', // Processing
                        '#ef4444', // Failed
                        '#6b7280'  // Pending
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            };
        }
        
        throw new Error(response.message);
    }

    /**
     * Load system performance data
     */
    async loadSystemPerformanceData() {
        const response = await this.apiClient.getPerformanceMetrics();
        
        if (response.success) {
            return {
                labels: response.data.labels,
                datasets: [
                    {
                        label: 'CPU',
                        data: response.data.cpu,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Memory',
                        data: response.data.memory,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Disk',
                        data: response.data.disk,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4
                    }
                ]
            };
        }
        
        throw new Error(response.message);
    }

    /**
     * Load upload activity data
     */
    async loadUploadActivityData() {
        // Mock data for upload activity
        const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);
        const uploads = Array.from({ length: 24 }, () => Math.floor(Math.random() * 50));
        
        return {
            labels: hours,
            datasets: [{
                label: 'آپلودها',
                data: uploads,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                fill: true,
                tension: 0.4
            }]
        };
    }

    /**
     * Update chart
     */
    updateChart(chartType, data) {
        const chart = this.charts.get(chartType);
        if (!chart) return;

        chart.data.labels = data.labels;
        chart.data.datasets = data.datasets;
        chart.update('active');
    }

    /**
     * Show chart error
     */
    showChartError(chartType, message) {
        const canvas = document.getElementById(`${chartType}-chart`);
        if (!canvas) return;

        const container = canvas.parentElement;
        if (!container) return;

        container.innerHTML = `
            <div class="chart-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>خطا در بارگذاری نمودار</p>
                <small>${message}</small>
                <button class="btn btn-sm btn-primary" onclick="chartManager.refreshChart('${chartType}')">
                    تلاش مجدد
                </button>
            </div>
        `;
    }

    /**
     * Handle data update
     */
    handleDataUpdate(data) {
        const { chartType, newData } = data;
        
        if (chartType && this.charts.has(chartType)) {
            this.updateChart(chartType, newData);
            this.dataCache.set(chartType, newData);
        }
    }

    /**
     * Refresh chart
     */
    async refreshChart(chartType) {
        console.log(`🔄 Refreshing chart: ${chartType}`);
        await this.loadChartData(chartType);
    }

    /**
     * Export chart
     */
    exportChart(chartType) {
        const chart = this.charts.get(chartType);
        if (!chart) return;

        const canvas = chart.canvas;
        const link = document.createElement('a');
        link.download = `${chartType}-chart.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
        
        this.showSuccess('خروجی موفق', 'نمودار با موفقیت دانلود شد');
    }

    /**
     * Change chart type
     */
    changeChartType(chartType, newType) {
        const chart = this.charts.get(chartType);
        if (!chart) return;

        const data = this.dataCache.get(chartType);
        if (!data) return;

        // Destroy current chart
        chart.destroy();

        // Create new chart with different type
        const canvas = document.getElementById(`${chartType}-chart`);
        const ctx = canvas.getContext('2d');
        
        const config = this.chartConfigs[chartType];
        config.type = newType;

        const newChart = new Chart(ctx, {
            type: newType,
            data: data,
            options: config.options
        });

        this.charts.set(chartType, newChart);
        
        console.log(`🔄 Changed chart type: ${chartType} -> ${newType}`);
    }

    /**
     * Start real-time updates
     */
    startRealTimeUpdates() {
        // Update system performance every 30 seconds
        this.updateIntervals.set('systemPerformance', setInterval(() => {
            this.refreshChart('systemPerformance');
        }, 30000));

        // Update upload activity every minute
        this.updateIntervals.set('uploadActivity', setInterval(() => {
            this.refreshChart('uploadActivity');
        }, 60000));

        // Update processing status every 2 minutes
        this.updateIntervals.set('processingStatus', setInterval(() => {
            this.refreshChart('processingStatus');
        }, 120000));

        console.log('🔄 Started real-time chart updates');
    }

    /**
     * Stop real-time updates
     */
    stopRealTimeUpdates() {
        this.updateIntervals.forEach((interval, chartType) => {
            clearInterval(interval);
            console.log(`⏹️ Stopped updates for: ${chartType}`);
        });
        this.updateIntervals.clear();
    }

    /**
     * Get chart statistics
     */
    getChartStats(chartType) {
        const data = this.dataCache.get(chartType);
        if (!data) return null;

        const values = data.datasets[0].data;
        
        return {
            total: values.reduce((sum, val) => sum + val, 0),
            average: values.reduce((sum, val) => sum + val, 0) / values.length,
            max: Math.max(...values),
            min: Math.min(...values)
        };
    }

    /**
     * Create custom chart
     */
    createCustomChart(canvasId, config) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, config);
        
        const chartId = `custom_${Date.now()}`;
        this.charts.set(chartId, chart);
        
        return chartId;
    }

    /**
     * Destroy chart
     */
    destroyChart(chartType) {
        const chart = this.charts.get(chartType);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartType);
            console.log(`🗑️ Destroyed chart: ${chartType}`);
        }

        // Stop real-time updates if any
        const interval = this.updateIntervals.get(chartType);
        if (interval) {
            clearInterval(interval);
            this.updateIntervals.delete(chartType);
        }
    }

    /**
     * Get all charts
     */
    getAllCharts() {
        return Array.from(this.charts.keys());
    }

    /**
     * Export all charts
     */
    exportAllCharts() {
        const promises = Array.from(this.charts.keys()).map(chartType => {
            return new Promise((resolve) => {
                const chart = this.charts.get(chartType);
                if (chart) {
                    const canvas = chart.canvas;
                    const link = document.createElement('a');
                    link.download = `${chartType}-chart.png`;
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    resolve(chartType);
                } else {
                    resolve(null);
                }
            });
        });

        Promise.all(promises).then(() => {
            this.showSuccess('خروجی موفق', 'تمام نمودارها دانلود شدند');
        });
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

// Initialize chart manager
const chartManager = new ChartManager();

// Export for use in other modules
window.ChartManager = ChartManager;
window.chartManager = chartManager;