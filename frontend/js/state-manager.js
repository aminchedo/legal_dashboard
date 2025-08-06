/**
 * State Manager for Legal Dashboard
 * ================================
 * 
 * Handles application state management, data persistence, reactive updates,
 * and cross-component communication across all modules.
 */

class StateManager {
    constructor() {
        this.state = {
            user: {
                profile: null,
                permissions: [],
                session: {
                    isAuthenticated: false,
                    token: null,
                    expiresAt: null
                }
            },
            documents: {
                list: [],
                filters: {
                    status: 'all',
                    type: 'all',
                    dateRange: null,
                    tags: [],
                    search: ''
                },
                sort: {
                    field: 'created_at',
                    direction: 'desc'
                },
                pagination: {
                    page: 1,
                    limit: 20,
                    total: 0
                },
                selection: new Set()
            },
            ui: {
                navigation: {
                    currentPage: '',
                    breadcrumbs: [],
                    activeMenuItem: null
                },
                modals: {
                    open: [],
                    active: null
                },
                notifications: {
                    queue: [],
                    unread: 0
                },
                theme: {
                    mode: 'light',
                    primaryColor: '#3b82f6'
                }
            },
            system: {
                health: {
                    api: 'online',
                    database: 'online',
                    storage: 'online',
                    lastCheck: Date.now()
                },
                performance: {
                    responseTime: 0,
                    memoryUsage: 0,
                    cpuUsage: 0
                },
                settings: {
                    autoSave: true,
                    notifications: true,
                    analytics: true
                }
            }
        };

        this.subscribers = new Map();
        this.persistentKeys = new Set([
            'user.profile',
            'user.permissions',
            'ui.theme',
            'system.settings'
        ]);
        this.eventBus = null;
        this.storagePrefix = 'legal_dashboard_';

        this.init();
    }

    /**
     * Initialize state manager
     */
    init() {
        this.eventBus = window.dashboardCore?.eventBus || new EventTarget();
        
        this.loadPersistentState();
        this.setupEventListeners();
        this.startPeriodicSync();
        
        console.log('🏗️ State Manager initialized');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for state change events
        this.eventBus?.addEventListener('state:change', (e) => {
            this.handleStateChange(e.detail);
        });

        // Listen for storage events (cross-tab sync)
        window.addEventListener('storage', (e) => {
            if (e.key && e.key.startsWith(this.storagePrefix)) {
                this.handleStorageChange(e);
            }
        });

        // Listen for beforeunload to save state
        window.addEventListener('beforeunload', () => {
            this.savePersistentState();
        });
    }

    /**
     * Get state value
     */
    get(path, defaultValue = null) {
        const keys = path.split('.');
        let current = this.state;

        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key];
            } else {
                return defaultValue;
            }
        }

        return current;
    }

    /**
     * Set state value
     */
    set(path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        let current = this.state;

        // Navigate to the parent object
        for (const key of keys) {
            if (!(key in current) || typeof current[key] !== 'object') {
                current[key] = {};
            }
            current = current[key];
        }

        // Set the value
        const oldValue = current[lastKey];
        current[lastKey] = value;

        // Notify subscribers
        this.notifySubscribers(path, value, oldValue);

        // Save to persistent storage if needed
        if (this.persistentKeys.has(path)) {
            this.saveToStorage(path, value);
        }

        // Broadcast state change
        this.broadcastStateChange(path, value, oldValue);

        return value;
    }

    /**
     * Update state value
     */
    update(path, updater) {
        const currentValue = this.get(path);
        const newValue = typeof updater === 'function' ? updater(currentValue) : updater;
        return this.set(path, newValue);
    }

    /**
     * Subscribe to state changes
     */
    subscribe(path, callback) {
        if (!this.subscribers.has(path)) {
            this.subscribers.set(path, new Set());
        }
        this.subscribers.get(path).add(callback);

        // Return unsubscribe function
        return () => {
            const callbacks = this.subscribers.get(path);
            if (callbacks) {
                callbacks.delete(callback);
                if (callbacks.size === 0) {
                    this.subscribers.delete(path);
                }
            }
        };
    }

    /**
     * Notify subscribers
     */
    notifySubscribers(path, newValue, oldValue) {
        const callbacks = this.subscribers.get(path);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, path);
                } catch (error) {
                    console.error('Error in state subscriber:', error);
                }
            });
        }

        // Also notify parent path subscribers
        const parentPath = this.getParentPath(path);
        if (parentPath) {
            const parentCallbacks = this.subscribers.get(parentPath);
            if (parentCallbacks) {
                parentCallbacks.forEach(callback => {
                    try {
                        callback(this.get(parentPath), null, parentPath);
                    } catch (error) {
                        console.error('Error in parent state subscriber:', error);
                    }
                });
            }
        }
    }

    /**
     * Get parent path
     */
    getParentPath(path) {
        const parts = path.split('.');
        if (parts.length > 1) {
            return parts.slice(0, -1).join('.');
        }
        return null;
    }

    /**
     * Broadcast state change
     */
    broadcastStateChange(path, newValue, oldValue) {
        this.eventBus?.dispatchEvent(new CustomEvent('state:changed', {
            detail: {
                path,
                newValue,
                oldValue,
                timestamp: Date.now()
            }
        }));
    }

    /**
     * Handle state change from other components
     */
    handleStateChange(detail) {
        const { path, value } = detail;
        this.set(path, value);
    }

    /**
     * Save to persistent storage
     */
    saveToStorage(path, value) {
        try {
            const key = this.storagePrefix + path.replace(/\./g, '_');
            localStorage.setItem(key, JSON.stringify({
                value,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.error('Error saving to storage:', error);
        }
    }

    /**
     * Load from persistent storage
     */
    loadFromStorage(path) {
        try {
            const key = this.storagePrefix + path.replace(/\./g, '_');
            const stored = localStorage.getItem(key);
            
            if (stored) {
                const data = JSON.parse(stored);
                return data.value;
            }
        } catch (error) {
            console.error('Error loading from storage:', error);
        }
        
        return null;
    }

    /**
     * Load persistent state
     */
    loadPersistentState() {
        this.persistentKeys.forEach(path => {
            const value = this.loadFromStorage(path);
            if (value !== null) {
                this.set(path, value);
            }
        });
    }

    /**
     * Save persistent state
     */
    savePersistentState() {
        this.persistentKeys.forEach(path => {
            const value = this.get(path);
            if (value !== null) {
                this.saveToStorage(path, value);
            }
        });
    }

    /**
     * Handle storage change (cross-tab sync)
     */
    handleStorageChange(event) {
        const path = event.key.replace(this.storagePrefix, '').replace(/_/g, '.');
        
        if (this.persistentKeys.has(path)) {
            try {
                const data = JSON.parse(event.newValue);
                this.set(path, data.value);
            } catch (error) {
                console.error('Error parsing storage change:', error);
            }
        }
    }

    /**
     * Start periodic sync
     */
    startPeriodicSync() {
        // Sync state every 30 seconds
        setInterval(() => {
            this.savePersistentState();
        }, 30000);

        // Health check every minute
        setInterval(() => {
            this.updateSystemHealth();
        }, 60000);
    }

    /**
     * Update system health
     */
    async updateSystemHealth() {
        try {
            const healthData = await this.checkSystemHealth();
            this.set('system.health', healthData);
        } catch (error) {
            console.error('Error updating system health:', error);
        }
    }

    /**
     * Check system health
     */
    async checkSystemHealth() {
        const apiClient = window.LegalDashboardAPI;
        if (!apiClient) return this.get('system.health');

        try {
            const response = await apiClient.healthCheck();
            return {
                api: response.success ? 'online' : 'offline',
                database: response.data?.database || 'unknown',
                storage: response.data?.storage || 'unknown',
                lastCheck: Date.now()
            };
        } catch (error) {
            return {
                api: 'offline',
                database: 'unknown',
                storage: 'unknown',
                lastCheck: Date.now()
            };
        }
    }

    /**
     * Reset state
     */
    reset(path = null) {
        if (path) {
            // Reset specific path
            const defaultValue = this.getDefaultValue(path);
            this.set(path, defaultValue);
        } else {
            // Reset entire state
            this.state = this.getInitialState();
            this.loadPersistentState();
            
            // Notify all subscribers
            this.subscribers.forEach((callbacks, path) => {
                callbacks.forEach(callback => {
                    try {
                        callback(this.get(path), null, path);
                    } catch (error) {
                        console.error('Error in state reset subscriber:', error);
                    }
                });
            });
        }
    }

    /**
     * Get default value for path
     */
    getDefaultValue(path) {
        const defaults = {
            'documents.filters': {
                status: 'all',
                type: 'all',
                dateRange: null,
                tags: [],
                search: ''
            },
            'documents.sort': {
                field: 'created_at',
                direction: 'desc'
            },
            'documents.pagination': {
                page: 1,
                limit: 20,
                total: 0
            },
            'documents.selection': new Set(),
            'ui.navigation.currentPage': '',
            'ui.navigation.breadcrumbs': [],
            'ui.navigation.activeMenuItem': null,
            'ui.modals.open': [],
            'ui.modals.active': null,
            'ui.notifications.queue': [],
            'ui.notifications.unread': 0
        };

        return defaults[path] || null;
    }

    /**
     * Get initial state
     */
    getInitialState() {
        return {
            user: {
                profile: null,
                permissions: [],
                session: {
                    isAuthenticated: false,
                    token: null,
                    expiresAt: null
                }
            },
            documents: {
                list: [],
                filters: {
                    status: 'all',
                    type: 'all',
                    dateRange: null,
                    tags: [],
                    search: ''
                },
                sort: {
                    field: 'created_at',
                    direction: 'desc'
                },
                pagination: {
                    page: 1,
                    limit: 20,
                    total: 0
                },
                selection: new Set()
            },
            ui: {
                navigation: {
                    currentPage: '',
                    breadcrumbs: [],
                    activeMenuItem: null
                },
                modals: {
                    open: [],
                    active: null
                },
                notifications: {
                    queue: [],
                    unread: 0
                },
                theme: {
                    mode: 'light',
                    primaryColor: '#3b82f6'
                }
            },
            system: {
                health: {
                    api: 'online',
                    database: 'online',
                    storage: 'online',
                    lastCheck: Date.now()
                },
                performance: {
                    responseTime: 0,
                    memoryUsage: 0,
                    cpuUsage: 0
                },
                settings: {
                    autoSave: true,
                    notifications: true,
                    analytics: true
                }
            }
        };
    }

    /**
     * Get state snapshot
     */
    getSnapshot() {
        return JSON.parse(JSON.stringify(this.state));
    }

    /**
     * Apply state snapshot
     */
    applySnapshot(snapshot) {
        this.state = JSON.parse(JSON.stringify(snapshot));
        
        // Notify all subscribers
        this.subscribers.forEach((callbacks, path) => {
            callbacks.forEach(callback => {
                try {
                    callback(this.get(path), null, path);
                } catch (error) {
                    console.error('Error in snapshot subscriber:', error);
                }
            });
        });
    }

    /**
     * Get state statistics
     */
    getStateStats() {
        return {
            totalSubscribers: Array.from(this.subscribers.values()).reduce((sum, set) => sum + set.size, 0),
            persistentKeys: this.persistentKeys.size,
            stateSize: JSON.stringify(this.state).length,
            lastUpdate: Date.now()
        };
    }

    /**
     * Debug state
     */
    debug() {
        console.log('🏗️ State Manager Debug Info:');
        console.log('Current State:', this.state);
        console.log('Subscribers:', this.subscribers);
        console.log('Persistent Keys:', this.persistentKeys);
        console.log('Stats:', this.getStateStats());
    }

    /**
     * Export state
     */
    exportState() {
        return {
            state: this.getSnapshot(),
            timestamp: Date.now(),
            version: '1.0.0'
        };
    }

    /**
     * Import state
     */
    importState(data) {
        if (data.state && data.version === '1.0.0') {
            this.applySnapshot(data.state);
            return true;
        }
        return false;
    }
}

// Initialize state manager
const stateManager = new StateManager();

// Export for use in other modules
window.StateManager = StateManager;
window.stateManager = stateManager;