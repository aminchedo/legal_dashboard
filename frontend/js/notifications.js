/**
 * Notification System for Legal Dashboard
 * ======================================
 * 
 * Handles real-time notifications, WebSocket connections, and notification management.
 */

class NotificationManager {
    constructor() {
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.notifications = [];
        this.unreadCount = 0;
        this.isConnected = false;
        this.userId = null;

        // Initialize notification elements
        this.initElements();

        // Start WebSocket connection
        this.connectWebSocket();

        // Set up periodic cleanup
        setInterval(() => this.cleanupExpiredNotifications(), 60000); // Every minute
    }

    initElements() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        // Create notification bell if it doesn't exist
        if (!document.getElementById('notification-bell')) {
            const bell = document.createElement('div');
            bell.id = 'notification-bell';
            bell.className = 'notification-bell';
            bell.innerHTML = `
                <i class="fas fa-bell"></i>
                <span class="notification-badge" id="notification-badge">0</span>
            `;
            bell.addEventListener('click', () => this.toggleNotificationPanel());
            document.body.appendChild(bell);
        }

        // Create notification panel if it doesn't exist
        if (!document.getElementById('notification-panel')) {
            const panel = document.createElement('div');
            panel.id = 'notification-panel';
            panel.className = 'notification-panel hidden';
            panel.innerHTML = `
                <div class="notification-header">
                    <h3>Notifications</h3>
                    <button class="close-btn" onclick="notificationManager.closeNotificationPanel()">×</button>
                </div>
                <div class="notification-list" id="notification-list"></div>
                <div class="notification-footer">
                    <button onclick="notificationManager.markAllAsRead()">Mark All as Read</button>
                    <button onclick="notificationManager.clearAll()">Clear All</button>
                </div>
            `;
            document.body.appendChild(panel);
        }

        // Add CSS styles
        this.addStyles();
    }

    addStyles() {
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                }
                
                .notification-bell {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #007bff;
                    color: white;
                    padding: 10px;
                    border-radius: 50%;
                    cursor: pointer;
                    z-index: 10001;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                }
                
                .notification-bell:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                }
                
                .notification-badge {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    background: #dc3545;
                    color: white;
                    border-radius: 50%;
                    padding: 2px 6px;
                    font-size: 12px;
                    min-width: 18px;
                    text-align: center;
                }
                
                .notification-panel {
                    position: fixed;
                    top: 70px;
                    right: 20px;
                    width: 350px;
                    max-height: 500px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    z-index: 10002;
                    overflow: hidden;
                    transition: all 0.3s ease;
                }
                
                .notification-panel.hidden {
                    transform: translateX(100%);
                    opacity: 0;
                }
                
                .notification-header {
                    padding: 15px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .notification-header h3 {
                    margin: 0;
                    color: #333;
                }
                
                .close-btn {
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                    color: #666;
                }
                
                .notification-list {
                    max-height: 350px;
                    overflow-y: auto;
                }
                
                .notification-item {
                    padding: 15px;
                    border-bottom: 1px solid #f0f0f0;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                }
                
                .notification-item:hover {
                    background-color: #f8f9fa;
                }
                
                .notification-item.unread {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                }
                
                .notification-title {
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #333;
                }
                
                .notification-message {
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 5px;
                }
                
                .notification-meta {
                    font-size: 12px;
                    color: #999;
                    display: flex;
                    justify-content: space-between;
                }
                
                .notification-footer {
                    padding: 15px;
                    border-top: 1px solid #eee;
                    display: flex;
                    gap: 10px;
                }
                
                .notification-footer button {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid #ddd;
                    background: white;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                }
                
                .notification-footer button:hover {
                    background: #f8f9fa;
                }
                
                .notification-toast {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    margin-bottom: 10px;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    animation: slideIn 0.3s ease;
                }
                
                .notification-toast.success {
                    border-left-color: #28a745;
                }
                
                .notification-toast.warning {
                    border-left-color: #ffc107;
                }
                
                .notification-toast.error {
                    border-left-color: #dc3545;
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                .notification-type-icon {
                    margin-right: 8px;
                }
                
                .notification-type-icon.info { color: #007bff; }
                .notification-type-icon.success { color: #28a745; }
                .notification-type-icon.warning { color: #ffc107; }
                .notification-type-icon.error { color: #dc3545; }
            `;
            document.head.appendChild(styles);
        }
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/notifications/ws`;

            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;

                // Send user authentication if available
                const token = localStorage.getItem('auth_token');
                if (token) {
                    this.websocket.send(JSON.stringify({
                        type: 'auth',
                        token: token
                    }));
                }
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleNotification(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.handleReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };

        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            this.handleReconnect();
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.showToast('Connection lost. Please refresh the page.', 'error');
        }
    }

    handleNotification(data) {
        if (data.type === 'connection_established') {
            console.log('Notification service connected');
            this.userId = data.user_id;
            return;
        }

        // Add notification to list
        const notification = {
            id: data.id || Date.now(),
            type: data.type || 'info',
            title: data.title || 'Notification',
            message: data.message || '',
            priority: data.priority || 'medium',
            created_at: data.created_at || new Date().toISOString(),
            metadata: data.metadata || {},
            read: false
        };

        this.notifications.unshift(notification);
        this.unreadCount++;
        this.updateBadge();
        this.showToast(notification);
        this.updateNotificationPanel();

        // Play notification sound if enabled
        this.playNotificationSound();
    }

    showToast(notification) {
        const container = document.getElementById('notification-container');
        const toast = document.createElement('div');
        toast.className = `notification-toast ${notification.type}`;

        const icon = this.getNotificationIcon(notification.type);

        toast.innerHTML = `
            <div class="notification-title">
                <i class="fas ${icon} notification-type-icon ${notification.type}"></i>
                ${notification.title}
            </div>
            <div class="notification-message">${notification.message}</div>
            <div class="notification-meta">
                <span>${this.formatTime(notification.created_at)}</span>
                <span>${notification.priority}</span>
            </div>
        `;

        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'upload_complete': 'fa-upload',
            'ocr_complete': 'fa-file-text',
            'scraping_complete': 'fa-spider',
            'system_error': 'fa-exclamation-circle',
            'user_activity': 'fa-user'
        };
        return icons[type] || 'fa-bell';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    updateBadge() {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'block' : 'none';
        }
    }

    toggleNotificationPanel() {
        const panel = document.getElementById('notification-panel');
        if (panel) {
            panel.classList.toggle('hidden');
            if (!panel.classList.contains('hidden')) {
                this.updateNotificationPanel();
            }
        }
    }

    closeNotificationPanel() {
        const panel = document.getElementById('notification-panel');
        if (panel) {
            panel.classList.add('hidden');
        }
    }

    updateNotificationPanel() {
        const list = document.getElementById('notification-list');
        if (!list) return;

        list.innerHTML = '';

        this.notifications.slice(0, 20).forEach(notification => {
            const item = document.createElement('div');
            item.className = `notification-item ${notification.read ? '' : 'unread'}`;
            item.onclick = () => this.markAsRead(notification.id);

            const icon = this.getNotificationIcon(notification.type);

            item.innerHTML = `
                <div class="notification-title">
                    <i class="fas ${icon} notification-type-icon ${notification.type}"></i>
                    ${notification.title}
                </div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-meta">
                    <span>${this.formatTime(notification.created_at)}</span>
                    <span>${notification.priority}</span>
                </div>
            `;

            list.appendChild(item);
        });
    }

    markAsRead(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification && !notification.read) {
            notification.read = true;
            this.unreadCount = Math.max(0, this.unreadCount - 1);
            this.updateBadge();
            this.updateNotificationPanel();

            // Send to server
            this.sendToServer('mark_read', { notification_id: notificationId });
        }
    }

    markAllAsRead() {
        this.notifications.forEach(notification => {
            notification.read = true;
        });
        this.unreadCount = 0;
        this.updateBadge();
        this.updateNotificationPanel();

        // Send to server
        this.sendToServer('mark_all_read', {});
    }

    clearAll() {
        this.notifications = [];
        this.unreadCount = 0;
        this.updateBadge();
        this.updateNotificationPanel();

        // Send to server
        this.sendToServer('clear_all', {});
    }

    sendToServer(action, data) {
        if (this.websocket && this.isConnected) {
            this.websocket.send(JSON.stringify({
                action: action,
                ...data
            }));
        }
    }

    playNotificationSound() {
        // Create audio context for notification sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);

            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            console.log('Could not play notification sound:', error);
        }
    }

    cleanupExpiredNotifications() {
        const now = new Date();
        const expired = this.notifications.filter(notification => {
            const created = new Date(notification.created_at);
            const diff = now - created;
            return diff > 24 * 60 * 60 * 1000; // 24 hours
        });

        expired.forEach(notification => {
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        });

        this.updateNotificationPanel();
    }

    // Public methods for external use
    showInfo(title, message, duration = 5000) {
        this.showCustomNotification('info', title, message, duration);
    }

    showSuccess(title, message, duration = 5000) {
        this.showCustomNotification('success', title, message, duration);
    }

    showWarning(title, message, duration = 5000) {
        this.showCustomNotification('warning', title, message, duration);
    }

    showError(title, message, duration = 5000) {
        this.showCustomNotification('error', title, message, duration);
    }

    showCustomNotification(type, title, message, duration) {
        const notification = {
            id: Date.now(),
            type: type,
            title: title,
            message: message,
            priority: 'medium',
            created_at: new Date().toISOString(),
            metadata: {},
            read: false
        };

        this.notifications.unshift(notification);
        this.unreadCount++;
        this.updateBadge();
        this.showToast(notification);
        this.updateNotificationPanel();

        if (duration > 0) {
            setTimeout(() => {
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                    this.updateNotificationPanel();
                }
            }, duration);
        }
    }
}

// Initialize notification manager when DOM is loaded
let notificationManager;

document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();
});

// Global function for external use
window.showNotification = (type, title, message) => {
    if (notificationManager) {
        notificationManager.showCustomNotification(type, title, message);
    }
}; 