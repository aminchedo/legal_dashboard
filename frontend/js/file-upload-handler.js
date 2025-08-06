/**
 * File Upload Handler for Legal Dashboard
 * Manages document uploads, OCR processing, and real-time progress
 */

class FileUploadHandler {
    constructor() {
        this.uploadEndpoint = '/api/ocr/upload';
        this.processEndpoint = '/api/ocr/process';
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];
        this.currentUpload = null;
        this.uploadQueue = [];

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input change
        const fileInput = document.getElementById('documentUpload');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
        }

        // Upload button
        const uploadBtn = document.getElementById('uploadButton');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.startUpload());
        }

        // Drag and drop
        const dropZone = document.getElementById('uploadDropZone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
            dropZone.addEventListener('drop', (e) => this.handleDrop(e));
            dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        }
    }

    handleFileSelection(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.validateAndQueueFiles(files);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.validateAndQueueFiles(files);
        }
    }

    validateAndQueueFiles(files) {
        const validFiles = [];
        const errors = [];

        for (let file of files) {
            // Check file size
            if (file.size > this.maxFileSize) {
                errors.push(`${file.name}: File too large (max 10MB)`);
                continue;
            }

            // Check file type
            if (!this.allowedTypes.includes(file.type)) {
                errors.push(`${file.name}: Unsupported file type`);
                continue;
            }

            validFiles.push(file);
        }

        // Show errors if any
        if (errors.length > 0) {
            this.showErrors(errors);
        }

        // Queue valid files
        if (validFiles.length > 0) {
            this.uploadQueue.push(...validFiles);
            this.updateUploadQueue();
        }
    }

    updateUploadQueue() {
        const queueContainer = document.getElementById('uploadQueue');
        if (!queueContainer) return;

        if (this.uploadQueue.length === 0) {
            queueContainer.innerHTML = '<p class="no-files">هیچ فایلی برای آپلود انتخاب نشده</p>';
            return;
        }

        const queueHTML = this.uploadQueue.map((file, index) => `
            <div class="queue-item" data-index="${index}">
                <div class="file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
                <div class="file-actions">
                    <button class="remove-file" onclick="fileUploadHandler.removeFromQueue(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `).join('');

        queueContainer.innerHTML = queueHTML;
    }

    removeFromQueue(index) {
        this.uploadQueue.splice(index, 1);
        this.updateUploadQueue();
    }

    async startUpload() {
        if (this.uploadQueue.length === 0) {
            this.showToast('لطفاً فایلی برای آپلود انتخاب کنید', 'warning');
            return;
        }

        if (this.currentUpload) {
            this.showToast('آپلود در حال انجام است، لطفاً صبر کنید', 'warning');
            return;
        }

        this.currentUpload = true;
        this.showUploadProgress();

        try {
            for (let i = 0; i < this.uploadQueue.length; i++) {
                const file = this.uploadQueue[i];
                await this.uploadFile(file, i + 1, this.uploadQueue.length);
            }

            this.showToast('تمام فایل‌ها با موفقیت آپلود شدند', 'success');
            this.refreshDocumentsList();
        } catch (error) {
            this.showToast(`خطا در آپلود: ${error.message}`, 'error');
        } finally {
            this.currentUpload = false;
            this.hideUploadProgress();
            this.uploadQueue = [];
            this.updateUploadQueue();
        }
    }

    async uploadFile(file, current, total) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('filename', file.name);

            const xhr = new XMLHttpRequest();

            // Progress tracking
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete, current, total);
                }
            });

            // Response handling
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        this.handleUploadSuccess(response, file);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('Invalid response format'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error during upload'));
            });

            xhr.addEventListener('abort', () => {
                reject(new Error('Upload cancelled'));
            });

            // Start upload
            xhr.open('POST', this.uploadEndpoint);
            xhr.send(formData);
        });
    }

    handleUploadSuccess(response, file) {
        // Update dashboard stats
        this.updateDashboardStats();

        // Show success message
        this.showToast(`${file.name} با موفقیت آپلود شد`, 'success');

        // Process OCR if needed
        if (response.document_id) {
            this.processOCR(response.document_id, file.name);
        }
    }

    async processOCR(documentId, fileName) {
        try {
            const response = await fetch(this.processEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    document_id: documentId,
                    filename: fileName
                })
            });

            if (!response.ok) {
                throw new Error(`OCR processing failed: ${response.status}`);
            }

            const result = await response.json();
            this.showOCRResult(result, fileName);
        } catch (error) {
            this.showToast(`خطا در پردازش OCR: ${error.message}`, 'error');
        }
    }

    showOCRResult(result, fileName) {
        const ocrResultsContainer = document.getElementById('ocrResults');
        if (!ocrResultsContainer) return;

        const resultHTML = `
            <div class="ocr-result">
                <h4>نتایج OCR - ${fileName}</h4>
                <div class="ocr-content">
                    <p><strong>کیفیت:</strong> ${(result.quality || 0).toFixed(2)}%</p>
                    <p><strong>متن استخراج شده:</strong></p>
                    <div class="extracted-text">
                        ${result.text || 'متنی استخراج نشد'}
                    </div>
                </div>
            </div>
        `;

        ocrResultsContainer.insertAdjacentHTML('afterbegin', resultHTML);
    }

    updateProgress(percent, current, total) {
        const progressBar = document.getElementById('uploadProgressBar');
        const progressText = document.getElementById('uploadProgressText');

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        if (progressText) {
            progressText.textContent = `آپلود فایل ${current} از ${total} (${Math.round(percent)}%)`;
        }
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }
    }

    hideUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    updateDashboardStats() {
        // Trigger dashboard stats refresh
        if (typeof loadDashboardStats === 'function') {
            loadDashboardStats();
        }
    }

    refreshDocumentsList() {
        // Trigger documents list refresh
        if (typeof loadDocumentsList === 'function') {
            loadDocumentsList();
        }
    }

    showErrors(errors) {
        const errorMessage = errors.join('\n');
        this.showToast(errorMessage, 'error');
    }

    showToast(message, type = 'info') {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize file upload handler
const fileUploadHandler = new FileUploadHandler(); 