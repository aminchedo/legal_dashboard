/**
 * Performance Optimization Utilities
 * ==================================
 * 
 * Utility functions and classes for optimizing frontend performance
 * including lazy loading, virtual scrolling, and resource management.
 */

/**
 * Virtual Scrolling for Large Lists
 */
class VirtualScrollManager {
    constructor(container, itemHeight, renderItem, data = []) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.data = data;

        this.visibleStart = 0;
        this.visibleEnd = 0;
        this.totalHeight = 0;
        this.viewportHeight = 0;
        this.scrollTop = 0;

        this.init();
    }

    init() {
        this.container.style.overflow = 'auto';
        this.container.style.position = 'relative';

        // Create viewport
        this.viewport = document.createElement('div');
        this.viewport.style.position = 'absolute';
        this.viewport.style.top = '0';
        this.viewport.style.left = '0';
        this.viewport.style.right = '0';
        this.container.appendChild(this.viewport);

        // Setup scroll handler
        this.container.addEventListener('scroll', () => this.handleScroll());

        // Setup resize observer
        if (window.ResizeObserver) {
            this.resizeObserver = new ResizeObserver(() => this.handleResize());
            this.resizeObserver.observe(this.container);
        }

        this.updateDimensions();
        this.render();
    }

    updateDimensions() {
        this.viewportHeight = this.container.clientHeight;
        this.totalHeight = this.data.length * this.itemHeight;
        this.container.style.height = `${this.totalHeight}px`;
    }

    handleScroll() {
        this.scrollTop = this.container.scrollTop;
        this.render();
    }

    handleResize() {
        this.updateDimensions();
        this.render();
    }

    render() {
        const bufferSize = Math.ceil(this.viewportHeight / this.itemHeight) + 5;
        this.visibleStart = Math.max(0, Math.floor(this.scrollTop / this.itemHeight) - bufferSize);
        this.visibleEnd = Math.min(this.data.length, this.visibleStart + bufferSize * 2);

        // Clear viewport
        this.viewport.innerHTML = '';

        // Render visible items
        for (let i = this.visibleStart; i < this.visibleEnd; i++) {
            const item = this.renderItem(this.data[i], i);
            item.style.position = 'absolute';
            item.style.top = `${i * this.itemHeight}px`;
            item.style.height = `${this.itemHeight}px`;
            item.style.width = '100%';
            this.viewport.appendChild(item);
        }
    }

    updateData(newData) {
        this.data = newData;
        this.updateDimensions();
        this.render();
    }

    destroy() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
    }
}

/**
 * Image Lazy Loading Manager
 */
class ImageLazyLoader {
    constructor(options = {}) {
        this.options = {
            threshold: 0.1,
            rootMargin: '50px',
            placeholder: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjZjNmNGY2Ii8+CjxyZWN0IHg9IjEzIiB5PSIxMyIgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiBmaWxsPSIjZGJkYmRiIi8+Cjwvc3ZnPgo=',
            ...options
        };

        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                threshold: this.options.threshold,
                rootMargin: this.options.rootMargin
            }
        );

        this.loadedImages = new Set();
    }

    observe(img) {
        if (this.loadedImages.has(img.src)) {
            this.loadImage(img);
            return;
        }

        // Set placeholder
        const originalSrc = img.dataset.src || img.src;
        img.dataset.src = originalSrc;
        img.src = this.options.placeholder;
        img.classList.add('lazy-loading');

        this.observer.observe(img);
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadImage(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (!src) return;

        const newImg = new Image();
        newImg.onload = () => {
            img.src = src;
            img.classList.remove('lazy-loading');
            img.classList.add('lazy-loaded');
            this.loadedImages.add(src);
        };

        newImg.onerror = () => {
            img.classList.remove('lazy-loading');
            img.classList.add('lazy-error');
        };

        newImg.src = src;
    }

    disconnect() {
        this.observer.disconnect();
    }
}

/**
 * Resource Preloader
 */
class ResourcePreloader {
    constructor() {
        this.preloadQueue = [];
        this.isPreloading = false;
        this.preloadedResources = new Set();
    }

    preloadImage(src, priority = 'low') {
        if (this.preloadedResources.has(src)) {
            return Promise.resolve(src);
        }

        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.preloadedResources.add(src);
                resolve(src);
            };
            img.onerror = reject;

            // Set loading priority
            if (priority === 'high') {
                img.loading = 'eager';
            } else {
                img.loading = 'lazy';
            }

            img.src = src;
        });
    }

    preloadCSS(href) {
        if (this.preloadedResources.has(href)) {
            return Promise.resolve(href);
        }

        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = href;

            link.onload = () => {
                this.preloadedResources.add(href);
                resolve(href);
            };
            link.onerror = reject;

            document.head.appendChild(link);
        });
    }

    preloadScript(src) {
        if (this.preloadedResources.has(src)) {
            return Promise.resolve(src);
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = true;

            script.onload = () => {
                this.preloadedResources.add(src);
                resolve(src);
            };
            script.onerror = reject;

            document.head.appendChild(script);
        });
    }

    async preloadBatch(resources) {
        const promises = resources.map(resource => {
            switch (resource.type) {
                case 'image':
                    return this.preloadImage(resource.src, resource.priority);
                case 'css':
                    return this.preloadCSS(resource.href);
                case 'script':
                    return this.preloadScript(resource.src);
                default:
                    return Promise.resolve();
            }
        });

        return Promise.allSettled(promises);
    }
}

/**
 * Performance Monitor
 */
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.observers = new Map();
        this.startTime = performance.now();
    }

    startMeasure(name) {
        this.metrics.set(name, {
            start: performance.now(),
            marks: []
        });
    }

    mark(name, label = '') {
        const metric = this.metrics.get(name);
        if (metric) {
            metric.marks.push({
                label,
                timestamp: performance.now(),
                duration: performance.now() - metric.start
            });
        }
    }

    endMeasure(name) {
        const metric = this.metrics.get(name);
        if (metric) {
            metric.end = performance.now();
            metric.duration = metric.end - metric.start;
            return metric;
        }
        return null;
    }

    observeLCP() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('🎯 LCP:', lastEntry.startTime);
            });

            observer.observe({ entryTypes: ['largest-contentful-paint'] });
            this.observers.set('lcp', observer);
        }
    }

    observeFID() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    console.log('⚡ FID:', entry.processingStart - entry.startTime);
                }
            });

            observer.observe({ entryTypes: ['first-input'] });
            this.observers.set('fid', observer);
        }
    }

    observeCLS() {
        if ('PerformanceObserver' in window) {
            let clsValue = 0;
            let clsEntries = [];

            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsEntries.push(entry);
                        clsValue += entry.value;
                    }
                }
                console.log('📐 CLS:', clsValue);
            });

            observer.observe({ entryTypes: ['layout-shift'] });
            this.observers.set('cls', observer);
        }
    }

    getMetrics() {
        return {
            navigation: performance.getEntriesByType('navigation')[0],
            memory: 'memory' in performance ? performance.memory : null,
            customMetrics: Object.fromEntries(this.metrics)
        };
    }

    startMonitoring() {
        this.observeLCP();
        this.observeFID();
        this.observeCLS();

        console.log('📊 Performance monitoring started');
    }

    stopMonitoring() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

/**
 * Bundle Size Optimizer
 */
class BundleOptimizer {
    constructor() {
        this.loadedModules = new Set();
        this.modulePromises = new Map();
    }

    async loadModule(modulePath) {
        if (this.loadedModules.has(modulePath)) {
            return this.modulePromises.get(modulePath);
        }

        const promise = import(modulePath);
        this.modulePromises.set(modulePath, promise);
        this.loadedModules.add(modulePath);

        return promise;
    }

    async loadModuleWhenNeeded(modulePath, condition) {
        if (typeof condition === 'function' ? condition() : condition) {
            return this.loadModule(modulePath);
        }
        return null;
    }

    preconnect(domain) {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = domain;
        document.head.appendChild(link);
    }

    dns_prefetch(domain) {
        const link = document.createElement('link');
        link.rel = 'dns-prefetch';
        link.href = domain;
        document.head.appendChild(link);
    }
}

/**
 * Memory Management Utilities
 */
class MemoryManager {
    constructor() {
        this.cleanupCallbacks = [];
        this.intervalId = null;
        this.startMonitoring();
    }

    registerCleanup(callback) {
        this.cleanupCallbacks.push(callback);
    }

    cleanup() {
        this.cleanupCallbacks.forEach(callback => {
            try {
                callback();
            } catch (error) {
                console.error('Cleanup error:', error);
            }
        });

        // Force garbage collection if available (Chrome DevTools)
        if (window.gc) {
            window.gc();
        }
    }

    startMonitoring() {
        this.intervalId = setInterval(() => {
            if ('memory' in performance) {
                const memory = performance.memory;
                const usedPercent = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;

                if (usedPercent > 80) {
                    console.warn('⚠️ High memory usage detected:', usedPercent.toFixed(1) + '%');
                    this.cleanup();
                }
            }
        }, 30000); // Check every 30 seconds
    }

    stopMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Global instances
const imageLoader = new ImageLazyLoader();
const resourcePreloader = new ResourcePreloader();
const performanceMonitor = new PerformanceMonitor();
const bundleOptimizer = new BundleOptimizer();
const memoryManager = new MemoryManager();

// Auto-start performance monitoring
performanceMonitor.startMonitoring();

// Auto-setup lazy loading for existing images
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageLoader.observe(img);
    });
});

// Export utilities
window.PerformanceUtils = {
    VirtualScrollManager,
    ImageLazyLoader,
    ResourcePreloader,
    PerformanceMonitor,
    BundleOptimizer,
    MemoryManager,
    imageLoader,
    resourcePreloader,
    performanceMonitor,
    bundleOptimizer,
    memoryManager
};

console.log('⚡ Performance utilities loaded');
