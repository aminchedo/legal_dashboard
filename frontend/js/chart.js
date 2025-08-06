/**
 * Chart Manager for Legal Dashboard
 * مدیریت کامل Chart.js و نمودارها
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.isChartJSLoaded = false;
        this.loadingAttempts = 0;
        this.maxLoadingAttempts = 10;
        
        // Wait for Chart.js to load
        this.waitForChartJS();
    }

    /**
     * Wait for Chart.js to be available
     */
    async waitForChartJS() {
        console.log('📊 Waiting for Chart.js to load...');
        
        const checkInterval = setInterval(() => {
            this.loadingAttempts++;
            
            if (typeof Chart !== 'undefined') {
                this.isChartJSLoaded = true;
                clearInterval(checkInterval);
                console.log('✅ Chart.js loaded successfully');
                this.onChartJSReady();
            } else if (this.loadingAttempts >= this.maxLoadingAttempts) {
                clearInterval(checkInterval);
                console.warn('⚠️ Chart.js failed to load after maximum attempts');
                this.onChartJSFailed();
            }
        }, 500);
    }

    /**
     * Called when Chart.js is ready
     */
    onChartJSReady() {
        // Hide placeholders and show canvases
        this.showChartCanvases();
        
        // Initialize charts
        this.initializeAllCharts();
        
        // Notify other components
        if (window.notifications) {
            window.notifications.show('نمودارها بارگذاری شدند', 'success', 'Chart.js');
        }
    }

    /**
     * Called when Chart.js fails to load
     */
    onChartJSFailed() {
        console.error('❌ Chart.js could not be loaded');
        this.showChartPlaceholders();
        
        if (window.notifications) {
            window.notifications.show('Chart.js بارگذاری نشد - نمودارها غیرفعال', 'warning', 'هشدار');
        }
    }

    /**
     * Show chart canvases and hide placeholders
     */
    showChartCanvases() {
        // Hide all placeholders
        document.querySelectorAll('.chart-placeholder').forEach(placeholder => {
            placeholder.style.display = 'none';
        });

        // Show all canvases
        document.querySelectorAll('canvas[id$="Canvas"]').forEach(canvas => {
            canvas.style.display = 'block';
        });
    }

    /**
     * Show placeholders when Chart.js fails
     */
    showChartPlaceholders() {
        document.querySelectorAll('.chart-placeholder').forEach(placeholder => {
            placeholder.innerHTML = `
                <i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>
                <p>Chart.js بارگذاری نشد</p>
                <small>نمودارها در دسترس نیستند</small>
            `;
        });
    }

    /**
     * Initialize all charts
     */
    initializeAllCharts() {
        if (!this.isChartJSLoaded) {
            console.warn('Chart.js not loaded, cannot initialize charts');
            return;
        }

        try {
            // Performance Chart
            this.initializePerformanceChart();
            
            // Status Chart
            this.initializeStatusChart();
            
            console.log('📊 All charts initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing charts:', error);
        }
    }

    /**
     * Initialize performance chart
     */
    initializePerformanceChart() {
        const ctx = document.getElementById('performanceChartCanvas');
        if (!ctx) return;

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'],
                datasets: [
                    {
                        label: 'زمان پاسخ (ms)',
                        data: [120, 190, 300, 250, 200, 350, 180],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'CPU Usage (%)',
                        data: [25, 35, 45, 40, 30, 50, 28],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                family: 'Vazirmatn',
                                size: 12
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                family: 'Vazirmatn'
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    /**
     * Initialize status chart
     */
    initializeStatusChart() {
        const ctx = document.getElementById('statusChartCanvas');
        if (!ctx) return;

        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['API آنلاین', 'OCR آماده', 'PDF فعال', 'Cache فعال'],
                datasets: [{
                    data: [1, 1, 1, 1],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                    borderColor: '#ffffff',
                    borderWidth: 3,
                    hoverBorderWidth: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                family: 'Vazirmatn',
                                size: 11
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    /**
     * Update performance chart
     */
    updatePerformanceChart(period) {
        if (!this.isChartJSLoaded || !this.charts.performance) {
            if (window.notifications) {
                window.notifications.show('نمودارها در دسترس نیستند', 'warning', 'هشدار');
            }
            return;
        }

        const data = {
            daily: {
                labels: ['ساعت 6', 'ساعت 9', 'ساعت 12', 'ساعت 15', 'ساعت 18', 'ساعت 21', 'ساعت 24'],
                responseTime: [120, 150, 200, 180, 160, 140, 130],
                cpuUsage: [25, 30, 45, 40, 35, 28, 22]
            },
            weekly: {
                labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'],
                responseTime: [120, 190, 300, 250, 200, 350, 180],
                cpuUsage: [25, 35, 45, 40, 30, 50, 28]
            },
            monthly: {
                labels: ['هفته 1', 'هفته 2', 'هفته 3', 'هفته 4'],
                responseTime: [180, 220, 190, 210],
                cpuUsage: [35, 42, 38, 40]
            }
        };

        const selectedData = data[period] || data.weekly;
        
        this.charts.performance.data.labels = selectedData.labels;
        this.charts.performance.data.datasets[0].data = selectedData.responseTime;
        this.charts.performance.data.datasets[1].data = selectedData.cpuUsage;
        this.charts.performance.update('active');

        if (window.notifications) {
            const periodText = period === 'daily' ? 'روزانه' : period === 'weekly' ? 'هفتگی' : 'ماهانه';
            window.notifications.show(`نمودار به حالت ${periodText} تغییر کرد`, 'info', 'بروزرسانی');
        }
    }

    /**
     * Update status chart
     */
    updateStatusChart(type) {
        if (!this.isChartJSLoaded || !this.charts.status) {
            if (window.notifications) {
                window.notifications.show('نمودارها در دسترس نیستند', 'warning', 'هشدار');
            }
            return;
        }

        const data = {
            services: {
                labels: ['API آنلاین', 'OCR آماده', 'PDF فعال', 'Cache فعال'],
                data: [1, 1, 1, 1],
                colors: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            },
            endpoints: {
                labels: ['/health', '/api/ocr/*', '/system/status', '/api/docs'],
                data: [1, 1, 1, 1],
                colors: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6']
            }
        };

        const selectedData = data[type] || data.services;
        
        this.charts.status.data.labels = selectedData.labels;
        this.charts.status.data.datasets[0].data = selectedData.data;
        this.charts.status.data.datasets[0].backgroundColor = selectedData.colors;
        this.charts.status.update('active');

        if (window.notifications) {
            const typeText = type === 'services' ? 'سرویس‌ها' : 'endpoint ها';
            window.notifications.show(`نمودار به حالت ${typeText} تغییر کرد`, 'info', 'بروزرسانی');
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Check if charts are ready
     */
    areChartsReady() {
        return this.isChartJSLoaded && Object.keys(this.charts).length > 0;
    }
}

// Create global instance
window.chartManager = new ChartManager();

console.log('📊 Chart Manager loaded');