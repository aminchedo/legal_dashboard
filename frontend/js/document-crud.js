/**
 * Document CRUD Handler for Legal Dashboard
 * Manages Create, Read, Update, Delete operations for documents
 */

class DocumentCRUDHandler {
    constructor() {
        this.baseEndpoint = '/api/documents';
        this.documents = [];
        this.currentEditId = null;
        this.searchQuery = '';
        this.filters = {
            status: 'all',
            category: 'all',
            dateFrom: '',
            dateTo: ''
        };

        this.initializeEventListeners();
        this.loadDocuments();
    }

    initializeEventListeners() {
        // Create document button
        const createBtn = document.getElementById('createDocumentBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateModal());
        }

        // Search input
        const searchInput = document.getElementById('documentSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.filterDocuments();
            });
        }

        // Filter selects
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.filterDocuments();
            });
        }

        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filters.category = e.target.value;
                this.filterDocuments();
            });
        }

        // Date filters
        const dateFromFilter = document.getElementById('dateFromFilter');
        if (dateFromFilter) {
            dateFromFilter.addEventListener('change', (e) => {
                this.filters.dateFrom = e.target.value;
                this.filterDocuments();
            });
        }

        const dateToFilter = document.getElementById('dateToFilter');
        if (dateToFilter) {
            dateToFilter.addEventListener('change', (e) => {
                this.filters.dateTo = e.target.value;
                this.filterDocuments();
            });
        }
    }

    async loadDocuments() {
        try {
            const response = await fetchWithErrorHandling(this.baseEndpoint);
            this.documents = response.documents || [];
            this.renderDocuments();
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showToast('خطا در بارگذاری اسناد', 'error');
        }
    }

    async createDocument(documentData) {
        try {
            const response = await fetchWithErrorHandling(this.baseEndpoint, {
                method: 'POST',
                body: JSON.stringify(documentData)
            });

            this.showToast('سند با موفقیت ایجاد شد', 'success');
            this.loadDocuments();
            return response;
        } catch (error) {
            this.showToast(`خطا در ایجاد سند: ${error.message}`, 'error');
            throw error;
        }
    }

    async updateDocument(id, documentData) {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/${id}`, {
                method: 'PUT',
                body: JSON.stringify(documentData)
            });

            this.showToast('سند با موفقیت به‌روزرسانی شد', 'success');
            this.loadDocuments();
            return response;
        } catch (error) {
            this.showToast(`خطا در به‌روزرسانی سند: ${error.message}`, 'error');
            throw error;
        }
    }

    async deleteDocument(id) {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/${id}`, {
                method: 'DELETE'
            });

            this.showToast('سند با موفقیت حذف شد', 'success');
            this.loadDocuments();
            return response;
        } catch (error) {
            this.showToast(`خطا در حذف سند: ${error.message}`, 'error');
            throw error;
        }
    }

    async searchDocuments(query) {
        try {
            const response = await fetchWithErrorHandling(`${this.baseEndpoint}/search?q=${encodeURIComponent(query)}`);
            return response.results || [];
        } catch (error) {
            console.error('Search failed:', error);
            return [];
        }
    }

    renderDocuments() {
        const container = document.getElementById('documentsList');
        if (!container) return;

        if (this.documents.length === 0) {
            container.innerHTML = '<p class="no-documents">هیچ سندی یافت نشد</p>';
            return;
        }

        const documentsHTML = this.documents.map(doc => this.renderDocumentItem(doc)).join('');
        container.innerHTML = documentsHTML;
    }

    renderDocumentItem(doc) {
        const statusClass = this.getStatusClass(doc.status);
        const qualityColor = this.getQualityColor(doc.quality);

        return `
            <div class="document-item" data-id="${doc.id}">
                <div class="document-header">
                    <h4 class="document-title" data-id="${doc.id}">${doc.title}</h4>
                    <div class="document-actions">
                        <button class="btn-edit" onclick="documentCRUDHandler.editDocument(${doc.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-delete" onclick="documentCRUDHandler.confirmDelete(${doc.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="document-details">
                    <div class="document-info">
                        <span class="document-status ${statusClass}">${this.getStatusText(doc.status)}</span>
                        <span class="document-quality" style="color: ${qualityColor}">
                            کیفیت: ${(doc.quality || 0).toFixed(1)}%
                        </span>
                        <span class="document-date">${this.formatDate(doc.created_at)}</span>
                    </div>
                    <div class="document-content">
                        <p class="document-description">${doc.description || 'توضیحات موجود نیست'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    showCreateModal() {
        const modal = document.getElementById('createDocumentModal');
        if (modal) {
            modal.style.display = 'block';
            this.resetCreateForm();
        }
    }

    hideCreateModal() {
        const modal = document.getElementById('createDocumentModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    resetCreateForm() {
        const form = document.getElementById('createDocumentForm');
        if (form) {
            form.reset();
        }
    }

    async handleCreateDocument(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const documentData = {
            title: formData.get('title'),
            description: formData.get('description'),
            category: formData.get('category'),
            status: 'pending'
        };

        try {
            await this.createDocument(documentData);
            this.hideCreateModal();
        } catch (error) {
            console.error('Create document failed:', error);
        }
    }

    editDocument(id) {
        const document = this.documents.find(doc => doc.id === id);
        if (!document) return;

        this.currentEditId = id;
        this.showEditModal(document);
    }

    showEditModal(document) {
        const modal = document.getElementById('editDocumentModal');
        if (modal) {
            // Populate form fields
            const titleInput = modal.querySelector('#editTitle');
            const descriptionInput = modal.querySelector('#editDescription');
            const categoryInput = modal.querySelector('#editCategory');
            const statusInput = modal.querySelector('#editStatus');

            if (titleInput) titleInput.value = document.title;
            if (descriptionInput) descriptionInput.value = document.description || '';
            if (categoryInput) categoryInput.value = document.category || '';
            if (statusInput) statusInput.value = document.status || 'pending';

            modal.style.display = 'block';
        }
    }

    hideEditModal() {
        const modal = document.getElementById('editDocumentModal');
        if (modal) {
            modal.style.display = 'none';
            this.currentEditId = null;
        }
    }

    async handleEditDocument(event) {
        event.preventDefault();

        if (!this.currentEditId) return;

        const formData = new FormData(event.target);
        const documentData = {
            title: formData.get('title'),
            description: formData.get('description'),
            category: formData.get('category'),
            status: formData.get('status')
        };

        try {
            await this.updateDocument(this.currentEditId, documentData);
            this.hideEditModal();
        } catch (error) {
            console.error('Update document failed:', error);
        }
    }

    confirmDelete(id) {
        const document = this.documents.find(doc => doc.id === id);
        if (!document) return;

        const confirmed = confirm(`آیا از حذف سند "${document.title}" اطمینان دارید؟`);
        if (confirmed) {
            this.deleteDocument(id);
        }
    }

    filterDocuments() {
        let filtered = this.documents;

        // Apply search filter
        if (this.searchQuery) {
            filtered = filtered.filter(doc =>
                doc.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                (doc.description && doc.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
            );
        }

        // Apply status filter
        if (this.filters.status !== 'all') {
            filtered = filtered.filter(doc => doc.status === this.filters.status);
        }

        // Apply category filter
        if (this.filters.category !== 'all') {
            filtered = filtered.filter(doc => doc.category === this.filters.category);
        }

        // Apply date filters
        if (this.filters.dateFrom) {
            filtered = filtered.filter(doc =>
                new Date(doc.created_at) >= new Date(this.filters.dateFrom)
            );
        }

        if (this.filters.dateTo) {
            filtered = filtered.filter(doc =>
                new Date(doc.created_at) <= new Date(this.filters.dateTo)
            );
        }

        this.renderFilteredDocuments(filtered);
    }

    renderFilteredDocuments(filtered) {
        const container = document.getElementById('documentsList');
        if (!container) return;

        if (filtered.length === 0) {
            container.innerHTML = '<p class="no-results">هیچ نتیجه‌ای یافت نشد</p>';
            return;
        }

        const documentsHTML = filtered.map(doc => this.renderDocumentItem(doc)).join('');
        container.innerHTML = documentsHTML;
    }

    getStatusClass(status) {
        const statusMap = {
            'pending': 'status-pending',
            'processing': 'status-processing',
            'completed': 'status-completed',
            'error': 'status-error'
        };
        return statusMap[status] || 'status-unknown';
    }

    getStatusText(status) {
        const statusMap = {
            'pending': 'در انتظار',
            'processing': 'در حال پردازش',
            'completed': 'تکمیل شده',
            'error': 'خطا'
        };
        return statusMap[status] || 'نامشخص';
    }

    getQualityColor(quality) {
        if (quality >= 80) return '#28a745';
        if (quality >= 60) return '#ffc107';
        return '#dc3545';
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

// Initialize document CRUD handler
const documentCRUDHandler = new DocumentCRUDHandler(); 