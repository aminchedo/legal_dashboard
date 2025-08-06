/**
 * File Handler for Legal Dashboard
 * ===============================
 * 
 * Handles file upload/download operations, validation, progress tracking,
 * drag-and-drop functionality, and file processing status.
 */

class FileHandler {
    constructor() {
        this.uploadQueue = [];
        this.activeUploads = new Map();
        this.maxConcurrentUploads = 3;
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        this.allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp'
        ];
        this.apiClient = null;
        this.eventBus = null;

        this.init();
    }

    /**
     * Initialize file handler
     */
    init() {
        this.apiClient = window.LegalDashboardAPI || new LegalDashboardAPI();
        this.eventBus = window.dashboardCore?.eventBus || new EventTarget();
        
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.processUploadQueue();
        
        console.log('📁 File Handler initialized');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // File input change
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="file"]')) {
                this.handleFileSelection(e.target);
            }
        });

        // Upload button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-upload-trigger]')) {
                e.preventDefault();
                this.triggerFileInput();
            }
        });

        // Cancel upload
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-cancel-upload]')) {
                e.preventDefault();
                const uploadId = e.target.getAttribute('data-upload-id');
                this.cancelUpload(uploadId);
            }
        });

        // Retry upload
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-retry-upload]')) {
                e.preventDefault();
                const uploadId = e.target.getAttribute('data-upload-id');
                this.retryUpload(uploadId);
            }
        });
    }

    /**
     * Setup drag and drop
     */
    setupDragAndDrop() {
        const dropZones = document.querySelectorAll('[data-drop-zone]');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                this.handleFiles(files);
            });
        });

        // Global drag and drop
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                this.handleFiles(files);
            }
        });
    }

    /**
     * Trigger file input
     */
    triggerFileInput() {
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.click();
        } else {
            this.createFileInput();
        }
    }

    /**
     * Create file input if it doesn't exist
     */
    createFileInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = this.allowedTypes.join(',');
        input.style.display = 'none';
        
        input.addEventListener('change', (e) => {
            this.handleFileSelection(e.target);
        });
        
        document.body.appendChild(input);
        input.click();
    }

    /**
     * Handle file selection
     */
    handleFileSelection(input) {
        const files = Array.from(input.files);
        this.handleFiles(files);
        
        // Reset input
        input.value = '';
    }

    /**
     * Handle files
     */
    handleFiles(files) {
        const validFiles = files.filter(file => this.validateFile(file));
        
        if (validFiles.length === 0) {
            this.showError('خطا در فایل‌ها', 'هیچ فایل معتبری یافت نشد');
            return;
        }

        // Add to upload queue
        validFiles.forEach(file => {
            this.addToUploadQueue(file);
        });

        // Process queue
        this.processUploadQueue();
    }

    /**
     * Validate file
     */
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            this.showError('فایل بزرگ است', `${file.name} از حداکثر اندازه مجاز (50MB) بزرگتر است`);
            return false;
        }

        // Check file type
        if (!this.allowedTypes.includes(file.type)) {
            this.showError('نوع فایل نامعتبر', `${file.name} از نوع فایل‌های مجاز نیست`);
            return false;
        }

        // Check file name
        if (file.name.length > 255) {
            this.showError('نام فایل طولانی است', `${file.name} نام فایل خیلی طولانی است`);
            return false;
        }

        return true;
    }

    /**
     * Add file to upload queue
     */
    addToUploadQueue(file) {
        const uploadId = this.generateUploadId();
        const uploadItem = {
            id: uploadId,
            file: file,
            status: 'pending',
            progress: 0,
            error: null,
            startTime: null,
            endTime: null
        };

        this.uploadQueue.push(uploadItem);
        this.renderUploadItem(uploadItem);
        
        console.log(`📤 Added ${file.name} to upload queue`);
    }

    /**
     * Process upload queue
     */
    async processUploadQueue() {
        const pendingUploads = this.uploadQueue.filter(item => item.status === 'pending');
        const activeUploads = this.activeUploads.size;

        if (pendingUploads.length === 0 || activeUploads >= this.maxConcurrentUploads) {
            return;
        }

        const availableSlots = this.maxConcurrentUploads - activeUploads;
        const uploadsToStart = pendingUploads.slice(0, availableSlots);

        uploadsToStart.forEach(uploadItem => {
            this.startUpload(uploadItem);
        });
    }

    /**
     * Start upload
     */
    async startUpload(uploadItem) {
        uploadItem.status = 'uploading';
        uploadItem.startTime = Date.now();
        this.activeUploads.set(uploadItem.id, uploadItem);

        this.updateUploadItem(uploadItem);

        try {
            const formData = new FormData();
            formData.append('file', uploadItem.file);

            const response = await this.apiClient.uploadFiles([uploadItem.file], {
                onProgress: (progress) => {
                    uploadItem.progress = progress;
                    this.updateUploadProgress(uploadItem);
                }
            });

            if (response.success) {
                uploadItem.status = 'completed';
                uploadItem.endTime = Date.now();
                
                // Broadcast upload success
                this.eventBus?.dispatchEvent(new CustomEvent('document:uploaded', {
                    detail: {
                        document: response.data.document,
                        uploadId: uploadItem.id
                    }
                }));

                this.showSuccess('آپلود موفق', `${uploadItem.file.name} با موفقیت آپلود شد`);
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            uploadItem.status = 'failed';
            uploadItem.error = error.message;
            uploadItem.endTime = Date.now();
            
            this.showError('خطا در آپلود', `${uploadItem.file.name}: ${error.message}`);
        } finally {
            this.activeUploads.delete(uploadItem.id);
            this.updateUploadItem(uploadItem);
            this.processUploadQueue(); // Process next upload
        }
    }

    /**
     * Cancel upload
     */
    cancelUpload(uploadId) {
        const uploadItem = this.uploadQueue.find(item => item.id === uploadId);
        if (!uploadItem) return;

        if (uploadItem.status === 'uploading') {
            // Cancel active upload
            const activeUpload = this.activeUploads.get(uploadId);
            if (activeUpload) {
                // Abort the request if possible
                if (activeUpload.abortController) {
                    activeUpload.abortController.abort();
                }
                this.activeUploads.delete(uploadId);
            }
        }

        uploadItem.status = 'cancelled';
        this.updateUploadItem(uploadItem);
        
        console.log(`❌ Cancelled upload: ${uploadItem.file.name}`);
    }

    /**
     * Retry upload
     */
    retryUpload(uploadId) {
        const uploadItem = this.uploadQueue.find(item => item.id === uploadId);
        if (!uploadItem) return;

        uploadItem.status = 'pending';
        uploadItem.progress = 0;
        uploadItem.error = null;
        uploadItem.startTime = null;
        uploadItem.endTime = null;

        this.updateUploadItem(uploadItem);
        this.processUploadQueue();
    }

    /**
     * Generate upload ID
     */
    generateUploadId() {
        return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Render upload item
     */
    renderUploadItem(uploadItem) {
        const container = document.querySelector('.upload-queue') || this.createUploadQueue();
        
        const itemElement = document.createElement('div');
        itemElement.className = 'upload-item';
        itemElement.setAttribute('data-upload-id', uploadItem.id);
        itemElement.innerHTML = this.renderUploadItemHTML(uploadItem);
        
        container.appendChild(itemElement);
    }

    /**
     * Create upload queue container
     */
    createUploadQueue() {
        const container = document.createElement('div');
        container.className = 'upload-queue';
        container.innerHTML = '<h3>صف آپلود</h3>';
        
        const uploadSection = document.querySelector('.upload-section') || document.body;
        uploadSection.appendChild(container);
        
        return container;
    }

    /**
     * Render upload item HTML
     */
    renderUploadItemHTML(uploadItem) {
        const statusIcons = {
            pending: 'fas fa-clock',
            uploading: 'fas fa-upload',
            completed: 'fas fa-check-circle',
            failed: 'fas fa-exclamation-circle',
            cancelled: 'fas fa-times-circle'
        };

        const statusClasses = {
            pending: 'status-pending',
            uploading: 'status-uploading',
            completed: 'status-completed',
            failed: 'status-failed',
            cancelled: 'status-cancelled'
        };

        return `
            <div class="upload-item-content">
                <div class="upload-info">
                    <i class="${statusIcons[uploadItem.status]} ${statusClasses[uploadItem.status]}"></i>
                    <div class="upload-details">
                        <span class="upload-name">${uploadItem.file.name}</span>
                        <span class="upload-size">${this.formatFileSize(uploadItem.file.size)}</span>
                    </div>
                </div>
                
                <div class="upload-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${uploadItem.progress}%"></div>
                    </div>
                    <span class="progress-text">${uploadItem.progress}%</span>
                </div>
                
                <div class="upload-actions">
                    ${uploadItem.status === 'uploading' ? `
                        <button class="btn-icon" data-cancel-upload data-upload-id="${uploadItem.id}" title="لغو">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                    
                    ${uploadItem.status === 'failed' ? `
                        <button class="btn-icon" data-retry-upload data-upload-id="${uploadItem.id}" title="تلاش مجدد">
                            <i class="fas fa-redo"></i>
                        </button>
                    ` : ''}
                    
                    ${uploadItem.status === 'completed' ? `
                        <button class="btn-icon" onclick="fileHandler.removeUploadItem('${uploadItem.id}')" title="حذف">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
            
            ${uploadItem.error ? `
                <div class="upload-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>${uploadItem.error}</span>
                </div>
            ` : ''}
        `;
    }

    /**
     * Update upload item
     */
    updateUploadItem(uploadItem) {
        const itemElement = document.querySelector(`[data-upload-id="${uploadItem.id}"]`);
        if (itemElement) {
            itemElement.innerHTML = this.renderUploadItemHTML(uploadItem);
        }
    }

    /**
     * Update upload progress
     */
    updateUploadProgress(uploadItem) {
        const progressFill = document.querySelector(`[data-upload-id="${uploadItem.id}"] .progress-fill`);
        const progressText = document.querySelector(`[data-upload-id="${uploadItem.id}"] .progress-text`);
        
        if (progressFill) {
            progressFill.style.width = `${uploadItem.progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${uploadItem.progress}%`;
        }
    }

    /**
     * Remove upload item
     */
    removeUploadItem(uploadId) {
        const itemElement = document.querySelector(`[data-upload-id="${uploadId}"]`);
        if (itemElement) {
            itemElement.remove();
        }

        const index = this.uploadQueue.findIndex(item => item.id === uploadId);
        if (index > -1) {
            this.uploadQueue.splice(index, 1);
        }
    }

    /**
     * Download file
     */
    async downloadFile(fileId, fileName) {
        try {
            const response = await this.apiClient.downloadDocument(fileId);
            
            if (response.success) {
                // Create download link
                const link = document.createElement('a');
                link.href = response.data.downloadUrl;
                link.download = fileName;
                link.style.display = 'none';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                this.showSuccess('دانلود موفق', 'فایل با موفقیت دانلود شد');
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            this.showError('خطا در دانلود', error.message);
        }
    }

    /**
     * Download multiple files
     */
    async downloadMultipleFiles(fileIds) {
        try {
            this.showInfo('دانلود', 'در حال آماده‌سازی فایل‌ها...');
            
            const promises = fileIds.map(id => this.apiClient.downloadDocument(id));
            const responses = await Promise.allSettled(promises);
            
            const successfulDownloads = responses.filter(r => r.status === 'fulfilled');
            
            if (successfulDownloads.length > 0) {
                // Create zip file or individual downloads
                this.showSuccess('دانلود موفق', `${successfulDownloads.length} فایل آماده دانلود است`);
            } else {
                throw new Error('هیچ فایلی دانلود نشد');
            }
        } catch (error) {
            this.showError('خطا در دانلود گروهی', error.message);
        }
    }

    /**
     * Preview file
     */
    async previewFile(fileId, fileType) {
        try {
            const response = await this.apiClient.getDocument(fileId);
            
            if (response.success) {
                this.showFilePreview(response.data, fileType);
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            this.showError('خطا در پیش‌نمایش', error.message);
        }
    }

    /**
     * Show file preview
     */
    showFilePreview(file, fileType) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content file-preview-modal">
                <div class="modal-header">
                    <h3>${file.name}</h3>
                    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="file-preview">
                        ${this.renderFilePreview(file, fileType)}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="fileHandler.downloadFile('${file.id}', '${file.name}')">
                        <i class="fas fa-download"></i>
                        دانلود
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    /**
     * Render file preview
     */
    renderFilePreview(file, fileType) {
        if (fileType.startsWith('image/')) {
            return `<img src="${file.previewUrl || file.url}" alt="${file.name}" class="preview-image">`;
        } else if (fileType === 'application/pdf') {
            return `<iframe src="${file.previewUrl || file.url}" class="preview-pdf"></iframe>`;
        } else if (fileType.startsWith('text/')) {
            return `
                <div class="preview-text">
                    <pre>${file.content || 'محتوای فایل در دسترس نیست'}</pre>
                </div>
            `;
        } else {
            return `
                <div class="preview-unsupported">
                    <i class="fas fa-file"></i>
                    <p>پیش‌نمایش برای این نوع فایل پشتیبانی نمی‌شود</p>
                    <button class="btn btn-primary" onclick="fileHandler.downloadFile('${file.id}', '${file.name}')">
                        دانلود فایل
                    </button>
                </div>
            `;
        }
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Get upload statistics
     */
    getUploadStats() {
        const stats = {
            total: this.uploadQueue.length,
            pending: this.uploadQueue.filter(item => item.status === 'pending').length,
            uploading: this.uploadQueue.filter(item => item.status === 'uploading').length,
            completed: this.uploadQueue.filter(item => item.status === 'completed').length,
            failed: this.uploadQueue.filter(item => item.status === 'failed').length,
            cancelled: this.uploadQueue.filter(item => item.status === 'cancelled').length
        };

        return stats;
    }

    /**
     * Clear completed uploads
     */
    clearCompletedUploads() {
        const completedUploads = this.uploadQueue.filter(item => item.status === 'completed');
        completedUploads.forEach(upload => {
            this.removeUploadItem(upload.id);
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

// Initialize file handler
const fileHandler = new FileHandler();

// Export for use in other modules
window.FileHandler = FileHandler;
window.fileHandler = fileHandler;