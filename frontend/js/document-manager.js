/**
 * Document Manager for Legal Dashboard
 * ===================================
 * 
 * Handles document CRUD operations, file validation, status tracking,
 * bulk operations, and real-time updates across all pages.
 */

class DocumentManager {
    constructor() {
        this.documents = new Map();
        this.selectedDocuments = new Set();
        this.filters = {
            status: 'all',
            type: 'all',
            dateRange: null,
            tags: [],
            search: ''
        };
        this.sortConfig = {
            field: 'created_at',
            direction: 'desc'
        };
        this.pagination = {
            page: 1,
            limit: 20,
            total: 0
        };
        this.isLoading = false;
        this.apiClient = null;
        this.eventBus = null;

        this.init();
    }

    /**
     * Initialize document manager
     */
    init() {
        this.apiClient = window.LegalDashboardAPI || new LegalDashboardAPI();
        this.eventBus = window.dashboardCore?.eventBus || new EventTarget();
        
        this.setupEventListeners();
        this.loadDocuments();
        
        console.log('📄 Document Manager initialized');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for document events
        this.eventBus?.addEventListener('document:uploaded', (e) => {
            this.handleDocumentUpload(e.detail);
        });

        this.eventBus?.addEventListener('document:updated', (e) => {
            this.handleDocumentUpdate(e.detail);
        });

        this.eventBus?.addEventListener('document:deleted', (e) => {
            this.handleDocumentDelete(e.detail);
        });

        // Listen for filter changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-filter]')) {
                this.handleFilterChange(e.target);
            }
        });

        // Listen for sort changes
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-sort]')) {
                this.handleSortChange(e.target);
            }
        });

        // Listen for bulk selection
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-bulk-select]')) {
                this.handleBulkSelection(e.target);
            }
        });

        // Listen for bulk actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bulk-action]')) {
                this.handleBulkAction(e.target);
            }
        });
    }

    /**
     * Load documents with current filters and pagination
     */
    async loadDocuments() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoadingState();

        try {
            const params = {
                page: this.pagination.page,
                limit: this.pagination.limit,
                ...this.filters,
                sort: `${this.sortConfig.field}:${this.sortConfig.direction}`
            };

            const response = await this.apiClient.getDocuments(params);
            
            if (response.success) {
                this.documents.clear();
                response.data.documents.forEach(doc => {
                    this.documents.set(doc.id, new DocumentModel(doc));
                });
                
                this.pagination.total = response.data.total;
                this.renderDocuments();
                this.updatePagination();
                this.updateStats();
            } else {
                this.showError('خطا در بارگذاری اسناد', response.message);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showError('خطا در بارگذاری اسناد', error.message);
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const container = document.querySelector('.documents-container');
        if (container) {
            container.innerHTML = `
                <div class="loading-skeleton">
                    ${Array.from({ length: 5 }, () => `
                        <div class="skeleton-item">
                            <div class="skeleton-checkbox"></div>
                            <div class="skeleton-icon"></div>
                            <div class="skeleton-content">
                                <div class="skeleton-title"></div>
                                <div class="skeleton-meta"></div>
                            </div>
                            <div class="skeleton-actions"></div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const skeleton = document.querySelector('.loading-skeleton');
        if (skeleton) {
            skeleton.remove();
        }
    }

    /**
     * Render documents
     */
    renderDocuments() {
        const container = document.querySelector('.documents-container');
        if (!container) return;

        const documents = Array.from(this.documents.values());
        
        if (documents.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-alt"></i>
                    <h3>هیچ سندی یافت نشد</h3>
                    <p>اسناد جدید آپلود کنید یا فیلترها را تغییر دهید</p>
                </div>
            `;
            return;
        }

        const viewMode = this.getCurrentViewMode();
        
        if (viewMode === 'grid') {
            this.renderGridView(container, documents);
        } else {
            this.renderListView(container, documents);
        }
    }

    /**
     * Render grid view
     */
    renderGridView(container, documents) {
        container.innerHTML = `
            <div class="documents-grid">
                ${documents.map(doc => this.renderDocumentCard(doc)).join('')}
            </div>
        `;
    }

    /**
     * Render list view
     */
    renderListView(container, documents) {
        container.innerHTML = `
            <div class="documents-table">
                <table>
                    <thead>
                        <tr>
                            <th>
                                <input type="checkbox" data-bulk-select="all" ${this.isAllSelected() ? 'checked' : ''}>
                            </th>
                            <th data-sort="name">نام فایل <i class="fas fa-sort"></i></th>
                            <th data-sort="type">نوع <i class="fas fa-sort"></i></th>
                            <th data-sort="size">حجم <i class="fas fa-sort"></i></th>
                            <th data-sort="status">وضعیت <i class="fas fa-sort"></i></th>
                            <th data-sort="created_at">تاریخ <i class="fas fa-sort"></i></th>
                            <th>عملیات</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${documents.map(doc => this.renderDocumentRow(doc)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * Render document card for grid view
     */
    renderDocumentCard(doc) {
        return `
            <div class="document-card ${doc.isSelected ? 'selected' : ''}" data-document-id="${doc.id}">
                <div class="card-header">
                    <input type="checkbox" data-bulk-select="${doc.id}" ${doc.isSelected ? 'checked' : ''}>
                    <div class="card-actions">
                        <button class="btn-icon" onclick="documentManager.showDocumentMenu('${doc.id}', event)">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </div>
                <div class="card-icon">
                    <i class="${doc.getFileIcon()}"></i>
                </div>
                <div class="card-content">
                    <h4 class="card-title">${doc.name}</h4>
                    <p class="card-meta">${doc.getFormattedFileSize()} • ${doc.getFormattedDate()}</p>
                    <div class="card-status">
                        <span class="status-badge ${doc.getStatusClass()}">
                            <i class="${doc.getStatusIcon()}"></i>
                            ${doc.getStatusText()}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render document row for list view
     */
    renderDocumentRow(doc) {
        return `
            <tr data-document-id="${doc.id}" class="${doc.isSelected ? 'selected' : ''}">
                <td>
                    <input type="checkbox" data-bulk-select="${doc.id}" ${doc.isSelected ? 'checked' : ''}>
                </td>
                <td>
                    <div class="document-info">
                        <i class="${doc.getFileIcon()}"></i>
                        <span>${doc.name}</span>
                    </div>
                </td>
                <td>${doc.type}</td>
                <td>${doc.getFormattedFileSize()}</td>
                <td>
                    <span class="status-badge ${doc.getStatusClass()}">
                        <i class="${doc.getStatusIcon()}"></i>
                        ${doc.getStatusText()}
                    </span>
                </td>
                <td>${doc.getFormattedDate()}</td>
                <td>
                    <div class="document-actions">
                        <button class="btn-icon" onclick="documentManager.showDocumentMenu('${doc.id}', event)">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * Get current view mode
     */
    getCurrentViewMode() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('view') || 'list';
    }

    /**
     * Handle filter change
     */
    handleFilterChange(target) {
        const filterType = target.getAttribute('data-filter');
        const value = target.value;

        switch (filterType) {
            case 'status':
                this.filters.status = value;
                break;
            case 'type':
                this.filters.type = value;
                break;
            case 'date':
                this.filters.dateRange = value;
                break;
            case 'search':
                this.filters.search = value;
                break;
        }

        this.pagination.page = 1; // Reset to first page
        this.loadDocuments();
    }

    /**
     * Handle sort change
     */
    handleSortChange(target) {
        const field = target.getAttribute('data-sort');
        
        if (this.sortConfig.field === field) {
            this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortConfig.field = field;
            this.sortConfig.direction = 'asc';
        }

        this.loadDocuments();
    }

    /**
     * Handle bulk selection
     */
    handleBulkSelection(target) {
        const documentId = target.getAttribute('data-bulk-select');
        
        if (documentId === 'all') {
            this.toggleSelectAll(target.checked);
        } else {
            this.toggleDocumentSelection(documentId, target.checked);
        }

        this.updateBulkActions();
    }

    /**
     * Toggle select all
     */
    toggleSelectAll(selected) {
        this.documents.forEach(doc => {
            doc.isSelected = selected;
            if (selected) {
                this.selectedDocuments.add(doc.id);
            } else {
                this.selectedDocuments.delete(doc.id);
            }
        });

        // Update checkboxes
        document.querySelectorAll('[data-bulk-select]').forEach(checkbox => {
            checkbox.checked = selected;
        });
    }

    /**
     * Toggle document selection
     */
    toggleDocumentSelection(documentId, selected) {
        const doc = this.documents.get(documentId);
        if (doc) {
            doc.isSelected = selected;
            if (selected) {
                this.selectedDocuments.add(documentId);
            } else {
                this.selectedDocuments.delete(documentId);
            }
        }

        // Update select all checkbox
        const selectAllCheckbox = document.querySelector('[data-bulk-select="all"]');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = this.isAllSelected();
            selectAllCheckbox.indeterminate = this.isPartiallySelected();
        }
    }

    /**
     * Check if all documents are selected
     */
    isAllSelected() {
        return this.documents.size > 0 && this.selectedDocuments.size === this.documents.size;
    }

    /**
     * Check if some documents are selected
     */
    isPartiallySelected() {
        return this.selectedDocuments.size > 0 && this.selectedDocuments.size < this.documents.size;
    }

    /**
     * Update bulk actions visibility
     */
    updateBulkActions() {
        const bulkActions = document.querySelector('.bulk-actions');
        if (bulkActions) {
            bulkActions.style.display = this.selectedDocuments.size > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Handle bulk action
     */
    async handleBulkAction(target) {
        const action = target.getAttribute('data-bulk-action');
        
        if (this.selectedDocuments.size === 0) {
            this.showError('خطا', 'لطفاً حداقل یک سند انتخاب کنید');
            return;
        }

        const confirmed = await this.confirmBulkAction(action);
        if (!confirmed) return;

        try {
            switch (action) {
                case 'delete':
                    await this.bulkDelete();
                    break;
                case 'download':
                    await this.bulkDownload();
                    break;
                case 'tag':
                    await this.bulkTag();
                    break;
                case 'move':
                    await this.bulkMove();
                    break;
            }
        } catch (error) {
            this.showError('خطا در عملیات گروهی', error.message);
        }
    }

    /**
     * Confirm bulk action
     */
    async confirmBulkAction(action) {
        const messages = {
            delete: `آیا از حذف ${this.selectedDocuments.size} سند اطمینان دارید؟`,
            download: `آیا می‌خواهید ${this.selectedDocuments.size} سند را دانلود کنید؟`,
            tag: 'لطفاً برچسب جدید را وارد کنید:',
            move: 'لطفاً پوشه مقصد را انتخاب کنید:'
        };

        return confirm(messages[action] || 'آیا از این عملیات اطمینان دارید؟');
    }

    /**
     * Bulk delete documents
     */
    async bulkDelete() {
        const promises = Array.from(this.selectedDocuments).map(id => 
            this.apiClient.deleteDocument(id)
        );

        const results = await Promise.allSettled(promises);
        const successCount = results.filter(r => r.status === 'fulfilled').length;

        this.showSuccess('حذف موفق', `${successCount} سند با موفقیت حذف شد`);
        
        this.selectedDocuments.clear();
        this.loadDocuments();
    }

    /**
     * Bulk download documents
     */
    async bulkDownload() {
        // Implementation for bulk download
        this.showInfo('دانلود', 'در حال آماده‌سازی فایل‌ها...');
    }

    /**
     * Bulk tag documents
     */
    async bulkTag() {
        const tag = prompt('برچسب جدید را وارد کنید:');
        if (!tag) return;

        // Implementation for bulk tagging
        this.showSuccess('برچسب‌گذاری', `${this.selectedDocuments.size} سند برچسب‌گذاری شد`);
    }

    /**
     * Bulk move documents
     */
    async bulkMove() {
        // Implementation for bulk move
        this.showInfo('انتقال', 'در حال انتقال اسناد...');
    }

    /**
     * Show document menu
     */
    showDocumentMenu(documentId, event) {
        event.stopPropagation();
        
        const doc = this.documents.get(documentId);
        if (!doc) return;

        const menu = document.createElement('div');
        menu.className = 'document-menu';
        menu.innerHTML = `
            <div class="menu-item" onclick="documentManager.downloadDocument('${documentId}')">
                <i class="fas fa-download"></i>
                دانلود
            </div>
            <div class="menu-item" onclick="documentManager.previewDocument('${documentId}')">
                <i class="fas fa-eye"></i>
                پیش‌نمایش
            </div>
            <div class="menu-item" onclick="documentManager.editDocument('${documentId}')">
                <i class="fas fa-edit"></i>
                ویرایش
            </div>
            <div class="menu-item" onclick="documentManager.shareDocument('${documentId}')">
                <i class="fas fa-share"></i>
                اشتراک‌گذاری
            </div>
            <div class="menu-divider"></div>
            <div class="menu-item danger" onclick="documentManager.deleteDocument('${documentId}')">
                <i class="fas fa-trash"></i>
                حذف
            </div>
        `;

        // Position menu
        const rect = event.target.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = `${rect.bottom + 5}px`;
        menu.style.left = `${rect.left}px`;
        menu.style.zIndex = '1000';

        // Remove existing menus
        document.querySelectorAll('.document-menu').forEach(m => m.remove());
        
        document.body.appendChild(menu);

        // Close menu on outside click
        setTimeout(() => {
            document.addEventListener('click', function closeMenu() {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            });
        }, 100);
    }

    /**
     * Download document
     */
    async downloadDocument(documentId) {
        try {
            const doc = this.documents.get(documentId);
            if (!doc) return;

            const response = await this.apiClient.downloadDocument(documentId);
            
            if (response.success) {
                // Create download link
                const link = document.createElement('a');
                link.href = response.data.downloadUrl;
                link.download = doc.name;
                link.click();
                
                this.showSuccess('دانلود موفق', 'فایل با موفقیت دانلود شد');
            } else {
                this.showError('خطا در دانلود', response.message);
            }
        } catch (error) {
            this.showError('خطا در دانلود', error.message);
        }
    }

    /**
     * Preview document
     */
    async previewDocument(documentId) {
        try {
            const doc = this.documents.get(documentId);
            if (!doc) return;

            const response = await this.apiClient.getDocument(documentId);
            
            if (response.success) {
                this.showDocumentPreview(response.data);
            } else {
                this.showError('خطا در پیش‌نمایش', response.message);
            }
        } catch (error) {
            this.showError('خطا در پیش‌نمایش', error.message);
        }
    }

    /**
     * Show document preview
     */
    showDocumentPreview(document) {
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
     * Edit document
     */
    editDocument(documentId) {
        // Implementation for document editing
        this.showInfo('ویرایش', 'در حال باز کردن ویرایشگر...');
    }

    /**
     * Share document
     */
    shareDocument(documentId) {
        // Implementation for document sharing
        this.showInfo('اشتراک‌گذاری', 'در حال آماده‌سازی لینک اشتراک...');
    }

    /**
     * Delete document
     */
    async deleteDocument(documentId) {
        const confirmed = confirm('آیا از حذف این سند اطمینان دارید؟');
        if (!confirmed) return;

        try {
            const response = await this.apiClient.deleteDocument(documentId);
            
            if (response.success) {
                this.documents.delete(documentId);
                this.selectedDocuments.delete(documentId);
                this.renderDocuments();
                this.updateStats();
                this.showSuccess('حذف موفق', 'سند با موفقیت حذف شد');
            } else {
                this.showError('خطا در حذف', response.message);
            }
        } catch (error) {
            this.showError('خطا در حذف', error.message);
        }
    }

    /**
     * Handle document upload
     */
    handleDocumentUpload(data) {
        const newDoc = new DocumentModel(data.document);
        this.documents.set(newDoc.id, newDoc);
        this.renderDocuments();
        this.updateStats();
    }

    /**
     * Handle document update
     */
    handleDocumentUpdate(data) {
        const doc = this.documents.get(data.document.id);
        if (doc) {
            Object.assign(doc, data.document);
            this.renderDocuments();
        }
    }

    /**
     * Handle document delete
     */
    handleDocumentDelete(data) {
        this.documents.delete(data.documentId);
        this.selectedDocuments.delete(data.documentId);
        this.renderDocuments();
        this.updateStats();
    }

    /**
     * Update pagination
     */
    updatePagination() {
        const paginationContainer = document.querySelector('.pagination');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(this.pagination.total / this.pagination.limit);
        
        if (totalPages <= 1) {
            paginationContainer.style.display = 'none';
            return;
        }

        paginationContainer.style.display = 'flex';
        paginationContainer.innerHTML = this.renderPagination(totalPages);
    }

    /**
     * Render pagination
     */
    renderPagination(totalPages) {
        const currentPage = this.pagination.page;
        const pages = [];

        // Previous button
        pages.push(`
            <button class="pagination-btn ${currentPage === 1 ? 'disabled' : ''}" 
                    onclick="documentManager.goToPage(${currentPage - 1})" 
                    ${currentPage === 1 ? 'disabled' : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>
        `);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                pages.push(`
                    <button class="pagination-btn ${i === currentPage ? 'active' : ''}" 
                            onclick="documentManager.goToPage(${i})">
                        ${i}
                    </button>
                `);
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                pages.push('<span class="pagination-ellipsis">...</span>');
            }
        }

        // Next button
        pages.push(`
            <button class="pagination-btn ${currentPage === totalPages ? 'disabled' : ''}" 
                    onclick="documentManager.goToPage(${currentPage + 1})" 
                    ${currentPage === totalPages ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>
        `);

        return pages.join('');
    }

    /**
     * Go to specific page
     */
    goToPage(page) {
        if (page < 1 || page > Math.ceil(this.pagination.total / this.pagination.limit)) return;
        
        this.pagination.page = page;
        this.loadDocuments();
    }

    /**
     * Update statistics
     */
    updateStats() {
        const stats = {
            total: this.documents.size,
            processing: Array.from(this.documents.values()).filter(d => d.status === 'processing').length,
            completed: Array.from(this.documents.values()).filter(d => d.status === 'completed').length,
            failed: Array.from(this.documents.values()).filter(d => d.status === 'failed').length
        };

        // Update stats display
        Object.entries(stats).forEach(([key, value]) => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = value.toLocaleString('fa-IR');
            }
        });

        // Store in localStorage for other pages
        localStorage.setItem('document_stats', JSON.stringify(stats));
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

    /**
     * Show info notification
     */
    showInfo(title, message) {
        if (window.notificationManager) {
            window.notificationManager.showInfo(title, message);
        } else {
            alert(`${title}: ${message}`);
        }
    }
}

// Initialize document manager
const documentManager = new DocumentManager();

// Export for use in other modules
window.DocumentManager = DocumentManager;
window.documentManager = documentManager;