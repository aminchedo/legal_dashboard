/**
 * Navigation Manager for Legal Dashboard
 * ====================================
 * 
 * Handles unified navigation system across all pages with active state management,
 * breadcrumbs, mobile responsiveness, and keyboard navigation support.
 */

class NavigationManager {
    constructor() {
        this.currentPage = '';
        this.navigationHistory = [];
        this.breadcrumbs = [];
        this.isMobileMenuOpen = false;
        this.activeMenuItem = null;
        
        // Navigation configuration
        this.navConfig = {
            dashboard: {
                path: '/index.html',
                title: 'داشبورد',
                icon: 'fas fa-tachometer-alt',
                badge: null,
                children: []
            },
            documents: {
                path: '/documents.html',
                title: 'مدیریت اسناد',
                icon: 'fas fa-file-alt',
                badge: null,
                children: [
                    { path: '/documents.html?view=list', title: 'نمایش لیستی' },
                    { path: '/documents.html?view=grid', title: 'نمایش شبکه‌ای' },
                    { path: '/documents.html?filter=recent', title: 'اسناد اخیر' }
                ]
            },
            upload: {
                path: '/upload.html',
                title: 'آپلود فایل',
                icon: 'fas fa-cloud-upload-alt',
                badge: null,
                children: []
            },
            search: {
                path: '/search.html',
                title: 'جستجو',
                icon: 'fas fa-search',
                badge: null,
                children: [
                    { path: '/search.html?type=advanced', title: 'جستجوی پیشرفته' },
                    { path: '/search.html?type=quick', title: 'جستجوی سریع' }
                ]
            },
            analytics: {
                path: '/analytics.html',
                title: 'تحلیل و گزارش',
                icon: 'fas fa-chart-bar',
                badge: null,
                children: [
                    { path: '/analytics.html?report=performance', title: 'گزارش عملکرد' },
                    { path: '/analytics.html?report=usage', title: 'گزارش استفاده' }
                ]
            },
            systemHealth: {
                path: '/system-health.html',
                title: 'وضعیت سیستم',
                icon: 'fas fa-heartbeat',
                badge: null,
                children: []
            },
            settings: {
                path: '/settings.html',
                title: 'تنظیمات',
                icon: 'fas fa-cog',
                badge: null,
                children: [
                    { path: '/settings.html?tab=general', title: 'تنظیمات عمومی' },
                    { path: '/settings.html?tab=security', title: 'امنیت' },
                    { path: '/settings.html?tab=notifications', title: 'اعلان‌ها' }
                ]
            }
        };

        this.init();
    }

    /**
     * Initialize navigation system
     */
    init() {
        this.detectCurrentPage();
        this.setupEventListeners();
        this.updateNavigation();
        this.setupKeyboardNavigation();
        this.setupMobileNavigation();
        this.generateBreadcrumbs();
        
        console.log('🧭 Navigation Manager initialized');
    }

    /**
     * Detect current page from URL
     */
    detectCurrentPage() {
        const pathname = window.location.pathname;
        const searchParams = new URLSearchParams(window.location.search);
        
        // Extract page name from pathname
        const pageName = pathname.split('/').pop().replace('.html', '') || 'dashboard';
        
        this.currentPage = pageName;
        this.currentParams = Object.fromEntries(searchParams.entries());
        
        console.log(`📍 Current page detected: ${this.currentPage}`);
    }

    /**
     * Setup event listeners for navigation
     */
    setupEventListeners() {
        // Handle navigation clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-link')) {
                e.preventDefault();
                const link = e.target.closest('.nav-link');
                const href = link.getAttribute('href');
                const target = link.getAttribute('data-target');
                
                if (href) {
                    this.navigateTo(href);
                } else if (target) {
                    this.navigateTo(target);
                }
            }
        });

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.detectCurrentPage();
            this.updateNavigation();
            this.generateBreadcrumbs();
        });

        // Handle mobile menu toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('.mobile-menu-toggle')) {
                e.preventDefault();
                this.toggleMobileMenu();
            }
        });

        // Close mobile menu on outside click
        document.addEventListener('click', (e) => {
            if (this.isMobileMenuOpen && !e.target.closest('.sidebar') && !e.target.closest('.mobile-menu-toggle')) {
                this.closeMobileMenu();
            }
        });
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Alt + N for navigation menu
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                this.toggleMobileMenu();
            }

            // Escape to close mobile menu
            if (e.key === 'Escape' && this.isMobileMenuOpen) {
                this.closeMobileMenu();
            }

            // Arrow keys for navigation
            if (e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
                e.preventDefault();
                this.navigateWithKeyboard(e.key);
            }
        });
    }

    /**
     * Navigate with keyboard
     */
    navigateWithKeyboard(key) {
        const menuItems = Array.from(document.querySelectorAll('.nav-link'));
        const currentIndex = menuItems.findIndex(item => item.classList.contains('active'));
        
        let newIndex = currentIndex;
        
        if (key === 'ArrowLeft') {
            newIndex = currentIndex > 0 ? currentIndex - 1 : menuItems.length - 1;
        } else if (key === 'ArrowRight') {
            newIndex = currentIndex < menuItems.length - 1 ? currentIndex + 1 : 0;
        }
        
        if (newIndex !== currentIndex && menuItems[newIndex]) {
            menuItems[newIndex].click();
        }
    }

    /**
     * Setup mobile navigation
     */
    setupMobileNavigation() {
        // Create mobile menu toggle if it doesn't exist
        if (!document.querySelector('.mobile-menu-toggle')) {
            const toggle = document.createElement('button');
            toggle.className = 'mobile-menu-toggle';
            toggle.innerHTML = '<i class="fas fa-bars"></i>';
            toggle.setAttribute('aria-label', 'Toggle navigation menu');
            
            // Insert into header
            const header = document.querySelector('.header') || document.querySelector('header');
            if (header) {
                header.insertBefore(toggle, header.firstChild);
            }
        }

        // Add mobile-specific styles
        this.addMobileStyles();
    }

    /**
     * Add mobile-specific styles
     */
    addMobileStyles() {
        if (!document.getElementById('mobile-nav-styles')) {
            const styles = document.createElement('style');
            styles.id = 'mobile-nav-styles';
            styles.textContent = `
                @media (max-width: 768px) {
                    .mobile-menu-toggle {
                        display: block;
                        position: fixed;
                        top: 1rem;
                        right: 1rem;
                        z-index: 1001;
                        background: var(--primary-gradient);
                        color: white;
                        border: none;
                        border-radius: 50%;
                        width: 3rem;
                        height: 3rem;
                        font-size: 1.2rem;
                        cursor: pointer;
                        box-shadow: var(--shadow-md);
                        transition: var(--transition-smooth);
                    }

                    .mobile-menu-toggle:hover {
                        transform: scale(1.1);
                        box-shadow: var(--shadow-lg);
                    }

                    .sidebar {
                        transform: translateX(100%);
                        transition: var(--transition-smooth);
                    }

                    .sidebar.mobile-open {
                        transform: translateX(0);
                    }

                    .sidebar-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(0, 0, 0, 0.5);
                        z-index: 999;
                        opacity: 0;
                        visibility: hidden;
                        transition: var(--transition-smooth);
                    }

                    .sidebar-overlay.active {
                        opacity: 1;
                        visibility: visible;
                    }

                    .main-content {
                        margin-right: 0;
                        padding: 1rem;
                    }
                }

                @media (min-width: 769px) {
                    .mobile-menu-toggle {
                        display: none;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
    }

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
        this.isMobileMenuOpen = !this.isMobileMenuOpen;
        
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay') || this.createOverlay();
        
        if (this.isMobileMenuOpen) {
            sidebar?.classList.add('mobile-open');
            overlay?.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            sidebar?.classList.remove('mobile-open');
            overlay?.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    /**
     * Close mobile menu
     */
    closeMobileMenu() {
        this.isMobileMenuOpen = false;
        
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar?.classList.remove('mobile-open');
        overlay?.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * Create overlay for mobile menu
     */
    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.addEventListener('click', () => this.closeMobileMenu());
        document.body.appendChild(overlay);
        return overlay;
    }

    /**
     * Update navigation with active states
     */
    updateNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            const isActive = this.isCurrentPage(href);
            
            link.classList.toggle('active', isActive);
            
            if (isActive) {
                this.activeMenuItem = link;
                this.updateBreadcrumbs();
            }
        });

        this.updateBadges();
    }

    /**
     * Check if link is current page
     */
    isCurrentPage(href) {
        if (!href) return false;
        
        const url = new URL(href, window.location.origin);
        const currentUrl = new URL(window.location.href);
        
        return url.pathname === currentUrl.pathname;
    }

    /**
     * Update navigation badges
     */
    updateBadges() {
        // Update document count badge
        const documentBadge = document.querySelector('[data-badge="documents"]');
        if (documentBadge) {
            const count = this.getDocumentCount();
            if (count > 0) {
                documentBadge.textContent = count;
                documentBadge.style.display = 'inline';
            } else {
                documentBadge.style.display = 'none';
            }
        }

        // Update notification badge
        const notificationBadge = document.querySelector('[data-badge="notifications"]');
        if (notificationBadge) {
            const count = this.getNotificationCount();
            if (count > 0) {
                notificationBadge.textContent = count;
                notificationBadge.style.display = 'inline';
            } else {
                notificationBadge.style.display = 'none';
            }
        }
    }

    /**
     * Get document count from cache or API
     */
    getDocumentCount() {
        const cached = localStorage.getItem('document_count');
        return cached ? parseInt(cached) : 0;
    }

    /**
     * Get notification count from cache or API
     */
    getNotificationCount() {
        const cached = localStorage.getItem('notification_count');
        return cached ? parseInt(cached) : 0;
    }

    /**
     * Generate breadcrumbs
     */
    generateBreadcrumbs() {
        this.breadcrumbs = [];
        
        // Add home
        this.breadcrumbs.push({
            title: 'خانه',
            path: '/index.html',
            icon: 'fas fa-home'
        });

        // Add current page
        const currentNav = this.navConfig[this.currentPage];
        if (currentNav) {
            this.breadcrumbs.push({
                title: currentNav.title,
                path: currentNav.path,
                icon: currentNav.icon
            });
        }

        // Add sub-page if exists
        if (this.currentParams.view || this.currentParams.tab || this.currentParams.type) {
            const subPage = this.currentParams.view || this.currentParams.tab || this.currentParams.type;
            this.breadcrumbs.push({
                title: this.getSubPageTitle(subPage),
                path: window.location.href,
                icon: 'fas fa-angle-left'
            });
        }

        this.renderBreadcrumbs();
    }

    /**
     * Get sub-page title
     */
    getSubPageTitle(subPage) {
        const titles = {
            'list': 'نمایش لیستی',
            'grid': 'نمایش شبکه‌ای',
            'recent': 'اسناد اخیر',
            'advanced': 'جستجوی پیشرفته',
            'quick': 'جستجوی سریع',
            'performance': 'گزارش عملکرد',
            'usage': 'گزارش استفاده',
            'general': 'تنظیمات عمومی',
            'security': 'امنیت',
            'notifications': 'اعلان‌ها'
        };
        
        return titles[subPage] || subPage;
    }

    /**
     * Render breadcrumbs
     */
    renderBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb-container');
        if (!breadcrumbContainer) return;

        breadcrumbContainer.innerHTML = this.breadcrumbs.map((crumb, index) => {
            const isLast = index === this.breadcrumbs.length - 1;
            const separator = isLast ? '' : '<i class="fas fa-angle-left mx-2 text-gray-400"></i>';
            
            return `
                <a href="${crumb.path}" class="breadcrumb-item ${isLast ? 'active' : ''}" ${isLast ? 'aria-current="page"' : ''}>
                    <i class="${crumb.icon}"></i>
                    <span>${crumb.title}</span>
                </a>
                ${separator}
            `;
        }).join('');
    }

    /**
     * Update breadcrumbs
     */
    updateBreadcrumbs() {
        this.generateBreadcrumbs();
    }

    /**
     * Navigate to page
     */
    navigateTo(path) {
        // Add to history
        this.navigationHistory.push({
            path: window.location.pathname,
            timestamp: Date.now()
        });

        // Keep only last 10 entries
        if (this.navigationHistory.length > 10) {
            this.navigationHistory.shift();
        }

        // Navigate
        window.location.href = path;
    }

    /**
     * Get navigation history
     */
    getNavigationHistory() {
        return this.navigationHistory;
    }

    /**
     * Get current page info
     */
    getCurrentPageInfo() {
        return {
            page: this.currentPage,
            params: this.currentParams,
            breadcrumbs: this.breadcrumbs,
            timestamp: Date.now()
        };
    }

    /**
     * Set badge count for navigation item
     */
    setBadge(itemKey, count) {
        const badge = document.querySelector(`[data-badge="${itemKey}"]`);
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    /**
     * Highlight navigation item
     */
    highlightItem(itemKey, duration = 3000) {
        const item = document.querySelector(`[data-nav="${itemKey}"]`);
        if (item) {
            item.classList.add('highlight');
            setTimeout(() => {
                item.classList.remove('highlight');
            }, duration);
        }
    }
}

// Initialize navigation manager
const navigationManager = new NavigationManager();

// Export for use in other modules
window.NavigationManager = NavigationManager;
window.navigationManager = navigationManager;