/**
 * WebSocket Manager for Real-time Updates
 * ======================================
 * 
 * Manages WebSocket connections for real-time dashboard updates,
 * notifications, and live data synchronization across all pages.
 */

class WebSocketManager {
    constructor(options = {}) {
        this.options = {
            reconnectDelay: 1000,
            maxReconnectDelay: 30000,
            reconnectAttempts: 0,
            maxReconnectAttempts: 10,
            heartbeatInterval: 30000,
            autoReconnect: true,
            ...options
        };

        this.ws = null;
        this.isConnected = false;
        this.isConnecting = false;
        this.listeners = new Map();
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        this.messageQueue = [];

        // Event handlers
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);

        // Auto-connect when created
        this.connect();
    }

    /**
     * Establish WebSocket connection
     */
    connect() {
        if (this.isConnected || this.isConnecting) {
            return;
        }

        this.isConnecting = true;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            console.log('🔌 Connecting to WebSocket:', wsUrl);
            this.ws = new WebSocket(wsUrl);

            this.ws.addEventListener('open', this.onOpen);
            this.ws.addEventListener('message', this.onMessage);
            this.ws.addEventListener('close', this.onClose);
            this.ws.addEventListener('error', this.onError);

        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket open event
     */
    onOpen(event) {
        console.log('✅ WebSocket connected');
        this.isConnected = true;
        this.isConnecting = false;
        this.options.reconnectAttempts = 0;

        // Start heartbeat
        this.startHeartbeat();

        // Send queued messages
        this.flushMessageQueue();

        // Notify listeners
        this.emit('connected', { timestamp: Date.now() });

        // Show success notification
        this.showNotification('اتصال زنده برقرار شد', 'success');
    }

    /**
     * Handle incoming WebSocket messages
     */
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data.type);

            // Handle different message types
            switch (data.type) {
                case 'heartbeat':
                    this.handleHeartbeat(data);
                    break;

                case 'document_uploaded':
                    this.handleDocumentUpdate(data);
                    break;

                case 'document_processed':
                    this.handleDocumentProcessed(data);
                    break;

                case 'scraping_update':
                    this.handleScrapingUpdate(data);
                    break;

                case 'system_health':
                    this.handleSystemHealth(data);
                    break;

                case 'analytics_update':
                    this.handleAnalyticsUpdate(data);
                    break;

                case 'notification':
                    this.handleNotification(data);
                    break;

                case 'user_activity':
                    this.handleUserActivity(data);
                    break;

                default:
                    console.warn('Unknown message type:', data.type);
            }

            // Emit to custom listeners
            this.emit(data.type, data);

        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket close event
     */
    onClose(event) {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.isConnecting = false;

        // Stop heartbeat
        this.stopHeartbeat();

        // Notify listeners
        this.emit('disconnected', {
            code: event.code,
            reason: event.reason,
            timestamp: Date.now()
        });

        // Show notification
        this.showNotification('اتصال زنده قطع شد', 'warning');

        // Schedule reconnect if auto-reconnect is enabled
        if (this.options.autoReconnect && !event.wasClean) {
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket error event
     */
    onError(error) {
        console.error('❌ WebSocket error:', error);
        this.emit('error', { error, timestamp: Date.now() });
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.options.reconnectAttempts >= this.options.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.showNotification('اتصال زنده برقرار نشد - حداکثر تلاش انجام شد', 'error');
            return;
        }

        const delay = Math.min(
            this.options.reconnectDelay * Math.pow(2, this.options.reconnectAttempts),
            this.options.maxReconnectDelay
        );

        console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.options.reconnectAttempts + 1})`);

        this.reconnectTimer = setTimeout(() => {
            this.options.reconnectAttempts++;
            this.connect();
        }, delay);
    }

    /**
     * Start heartbeat mechanism
     */
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.send({
                    type: 'heartbeat',
                    timestamp: Date.now()
                });
            }
        }, this.options.heartbeatInterval);
    }

    /**
     * Stop heartbeat mechanism
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Send message through WebSocket
     */
    send(data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('❌ Error sending WebSocket message:', error);
                return false;
            }
        } else {
            // Queue message for later
            this.messageQueue.push(data);
            return false;
        }
    }

    /**
     * Flush queued messages
     */
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    /**
     * Add event listener
     */
    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }
        this.listeners.get(eventType).push(callback);
    }

    /**
     * Remove event listener
     */
    off(eventType, callback) {
        if (this.listeners.has(eventType)) {
            const callbacks = this.listeners.get(eventType);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    /**
     * Emit event to listeners
     */
    emit(eventType, data) {
        if (this.listeners.has(eventType)) {
            this.listeners.get(eventType).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('❌ Error in WebSocket event listener:', error);
                }
            });
        }
    }

    // ==================== MESSAGE HANDLERS ====================

    /**
     * Handle heartbeat response
     */
    handleHeartbeat(data) {
        // Heartbeat acknowledged - connection is alive
    }

    /**
     * Handle document upload updates
     */
    handleDocumentUpdate(data) {
        console.log('📄 Document update received:', data);

        // Update dashboard core
        if (window.dashboardCore) {
            window.dashboardCore.broadcast('documentUploaded', {
                fileId: data.document_id,
                fileName: data.filename,
                status: data.status,
                timestamp: data.timestamp
            });
        }

        // Show notification
        if (data.status === 'completed') {
            this.showNotification(`فایل "${data.filename}" آپلود شد`, 'success');
        }

        // Update document list if on documents page
        this.updateDocumentList();
    }

    /**
     * Handle document processing completion
     */
    handleDocumentProcessed(data) {
        console.log('⚙️ Document processed:', data);

        // Update dashboard core
        if (window.dashboardCore) {
            window.dashboardCore.broadcast('documentProcessed', {
                documentId: data.document_id,
                ocrText: data.ocr_text,
                qualityScore: data.quality_score,
                processingTime: data.processing_time
            });
        }

        // Show notification
        this.showNotification(`پردازش سند "${data.filename}" تکمیل شد`, 'success');

        // Update analytics if on dashboard
        this.updateDashboardStats();
    }

    /**
     * Handle scraping updates
     */
    handleScrapingUpdate(data) {
        console.log('🕷️ Scraping update:', data);

        // Update dashboard core
        if (window.dashboardCore) {
            window.dashboardCore.broadcast('scrapingUpdate', {
                jobId: data.job_id,
                status: data.status,
                progress: data.progress,
                totalItems: data.total_items,
                completedItems: data.completed_items
            });
        }

        // Show progress notification
        if (data.status === 'completed') {
            this.showNotification(`اسکرپینگ تکمیل شد: ${data.completed_items} آیتم`, 'success');
        } else if (data.status === 'failed') {
            this.showNotification(`خطا در اسکرپینگ: ${data.error}`, 'error');
        }

        // Update scraping dashboard if visible
        this.updateScrapingDashboard();
    }

    /**
     * Handle system health updates
     */
    handleSystemHealth(data) {
        console.log('💓 System health update:', data);

        // Update dashboard core
        if (window.dashboardCore) {
            window.dashboardCore.broadcast('healthUpdate', {
                status: data.status,
                services: data.services,
                metrics: data.metrics
            });
        }

        // Show warning for unhealthy status
        if (data.status !== 'healthy') {
            this.showNotification('هشدار سلامت سیستم', 'warning');
        }
    }

    /**
     * Handle analytics updates
     */
    handleAnalyticsUpdate(data) {
        console.log('📊 Analytics update:', data);

        // Update dashboard stats
        if (window.dashboard && typeof window.dashboard.updateRealTimeStatsOptimized === 'function') {
            window.dashboard.realTimeData = {
                ...window.dashboard.realTimeData,
                ...data.metrics
            };
            window.dashboard.updateRealTimeStatsOptimized();
        }

        // Update charts if visible
        if (window.dashboard && typeof window.dashboard.updateChartsOptimized === 'function') {
            window.dashboard.updateChartsOptimized();
        }
    }

    /**
     * Handle real-time notifications
     */
    handleNotification(data) {
        this.showNotification(data.message, data.type || 'info', data.duration);
    }

    /**
     * Handle user activity updates
     */
    handleUserActivity(data) {
        console.log('👤 User activity:', data);

        // Update user activity indicators
        this.updateUserActivity(data);
    }

    // ==================== UI UPDATE METHODS ====================

    /**
     * Update document list
     */
    updateDocumentList() {
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
    updateDashboardStats() {
        if (window.dashboard && typeof window.dashboard.loadDashboardData === 'function') {
            window.dashboard.debouncedUpdates.get('dashboard')();
        }
    }

    /**
     * Update scraping dashboard
     */
    updateScrapingDashboard() {
        if (typeof loadScrapingData === 'function') {
            loadScrapingData();
        }

        if (typeof updateScrapingStatus === 'function') {
            updateScrapingStatus();
        }
    }

    /**
     * Update user activity indicators
     */
    updateUserActivity(data) {
        // Update online users count
        const onlineUsersElement = document.getElementById('onlineUsers');
        if (onlineUsersElement && data.online_users) {
            onlineUsersElement.textContent = data.online_users;
        }

        // Update recent activity
        const activityElement = document.getElementById('recentActivity');
        if (activityElement && data.recent_activity) {
            this.updateActivityFeed(data.recent_activity);
        }
    }

    /**
     * Update activity feed
     */
    updateActivityFeed(activities) {
        const activityElement = document.getElementById('recentActivity');
        if (!activityElement) return;

        activities.forEach(activity => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            activityItem.innerHTML = `
                <div class="activity-icon">
                    <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-message">${activity.message}</div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            `;

            activityElement.insertBefore(activityItem, activityElement.firstChild);

            // Remove old activities (keep only last 10)
            while (activityElement.children.length > 10) {
                activityElement.removeChild(activityElement.lastChild);
            }
        });
    }

    /**
     * Get icon for activity type
     */
    getActivityIcon(type) {
        const icons = {
            'document_upload': 'cloud-upload-alt',
            'document_process': 'cogs',
            'scraping_start': 'spider',
            'scraping_complete': 'check-circle',
            'user_login': 'sign-in-alt',
            'user_logout': 'sign-out-alt',
            'system_alert': 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Format timestamp for display
     */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('fa-IR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Show notification
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
     * Close WebSocket connection
     */
    disconnect() {
        this.options.autoReconnect = false;

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        this.stopHeartbeat();

        if (this.ws) {
            this.ws.close(1000, 'Manual disconnect');
        }
    }

    /**
     * Get connection status
     */
    getStatus() {
        return {
            connected: this.isConnected,
            connecting: this.isConnecting,
            reconnectAttempts: this.options.reconnectAttempts,
            queuedMessages: this.messageQueue.length
        };
    }
}

// Global WebSocket instance
let wsManager = null;

// Initialize WebSocket when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if not already created
    if (!wsManager) {
        wsManager = new WebSocketManager({
            autoReconnect: true,
            maxReconnectAttempts: 10,
            heartbeatInterval: 30000
        });

        // Make available globally
        window.wsManager = wsManager;

        console.log('🔌 WebSocket Manager initialized');
    }
});

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
}

// Make available globally
window.WebSocketManager = WebSocketManager;

console.log('📡 WebSocket Manager loaded');
