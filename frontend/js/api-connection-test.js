/**
 * API Connection Test Script
 * =========================
 * 
 * Automated test script to validate all backend API endpoints
 * and provide detailed reporting on frontend-backend integration.
 */

class APIConnectionTester {
    constructor() {
        this.baseURL = window.location.origin;
        this.results = [];
        this.startTime = null;
        this.endTime = null;
    }

    /**
     * Run comprehensive API tests
     */
    async runAllTests() {
        console.log('🚀 Starting API Connection Tests...');
        this.startTime = Date.now();

        const tests = [
            // System Health Tests
            { name: 'Health Check', url: '/api/health', method: 'GET', category: 'System' },

            // Dashboard Tests
            { name: 'Dashboard Summary', url: '/api/dashboard/summary', method: 'GET', category: 'Dashboard' },
            { name: 'Charts Data', url: '/api/dashboard/charts-data', method: 'GET', category: 'Dashboard' },
            { name: 'AI Suggestions', url: '/api/dashboard/ai-suggestions', method: 'GET', category: 'Dashboard' },
            { name: 'Performance Metrics', url: '/api/dashboard/performance-metrics', method: 'GET', category: 'Dashboard' },
            { name: 'Trends', url: '/api/dashboard/trends', method: 'GET', category: 'Dashboard' },

            // Documents Tests
            { name: 'Documents List', url: '/api/documents?limit=5', method: 'GET', category: 'Documents' },
            { name: 'Document Categories', url: '/api/documents/categories/', method: 'GET', category: 'Documents' },
            { name: 'Document Sources', url: '/api/documents/sources/', method: 'GET', category: 'Documents' },
            { name: 'Document Search', url: '/api/documents/search/?q=test', method: 'GET', category: 'Documents' },

            // OCR Tests
            { name: 'OCR Status', url: '/api/ocr/status', method: 'GET', category: 'OCR' },
            { name: 'OCR Models', url: '/api/ocr/models', method: 'GET', category: 'OCR' },

            // Analytics Tests
            { name: 'Analytics Overview', url: '/api/analytics/overview', method: 'GET', category: 'Analytics' },
            { name: 'Analytics Performance', url: '/api/analytics/performance', method: 'GET', category: 'Analytics' },
            { name: 'Analytics Entities', url: '/api/analytics/entities?limit=10', method: 'GET', category: 'Analytics' },
            { name: 'Analytics Quality', url: '/api/analytics/quality-analysis', method: 'GET', category: 'Analytics' },

            // Scraping Tests
            { name: 'Scraping Statistics', url: '/api/scraping/statistics', method: 'GET', category: 'Scraping' },
            { name: 'Scraping Status', url: '/api/scraping/status', method: 'GET', category: 'Scraping' },
            { name: 'Rating Summary', url: '/api/scraping/rating/summary', method: 'GET', category: 'Scraping' },
            { name: 'Scraping Health', url: '/api/scraping/health', method: 'GET', category: 'Scraping' },

            // Phase 2 - File Upload Tests
            { name: 'OCR Upload', url: '/api/ocr/upload', method: 'POST', category: 'File Upload' },
            { name: 'OCR Process', url: '/api/ocr/process', method: 'POST', category: 'File Upload' },
            { name: 'OCR Quality Metrics', url: '/api/ocr/quality-metrics', method: 'GET', category: 'File Upload' },

            // Phase 2 - Document Management Tests
            { name: 'Create Document', url: '/api/documents', method: 'POST', category: 'Document Management' },
            { name: 'Update Document', url: '/api/documents/1', method: 'PUT', category: 'Document Management' },
            { name: 'Delete Document', url: '/api/documents/1', method: 'DELETE', category: 'Document Management' },

            // Phase 2 - Advanced Scraping Tests
            { name: 'Scraping Start', url: '/api/scraping/start', method: 'POST', category: 'Advanced Scraping' },
            { name: 'Scraping Stop', url: '/api/scraping/stop', method: 'POST', category: 'Advanced Scraping' },
            { name: 'Scraping Results', url: '/api/scraping/results', method: 'GET', category: 'Advanced Scraping' }
        ];

        console.log(`📋 Running ${tests.length} API tests...`);

        for (const test of tests) {
            await this.runSingleTest(test);
            // Small delay to avoid overwhelming the server
            await this.delay(100);
        }

        this.endTime = Date.now();
        this.generateReport();
    }

    /**
     * Run a single API test
     */
    async runSingleTest(test) {
        const startTime = Date.now();
        let result = {
            name: test.name,
            category: test.category,
            url: test.url,
            method: test.method,
            success: false,
            status: null,
            responseTime: 0,
            data: null,
            error: null,
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch(test.url, {
                method: test.method,
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            result.status = response.status;
            result.responseTime = Date.now() - startTime;

            if (response.ok) {
                result.success = true;
                try {
                    result.data = await response.json();
                } catch (e) {
                    result.data = 'Non-JSON response';
                }
            } else {
                result.error = `${response.status}: ${response.statusText}`;
            }

        } catch (error) {
            result.error = error.message;
            result.responseTime = Date.now() - startTime;
        }

        this.results.push(result);

        // Log result
        const status = result.success ? '✅' : '❌';
        console.log(`${status} ${test.name}: ${result.success ? 'PASS' : 'FAIL'} (${result.responseTime}ms)`);

        return result;
    }

    /**
     * Generate comprehensive test report
     */
    generateReport() {
        const totalTests = this.results.length;
        const passedTests = this.results.filter(r => r.success).length;
        const failedTests = totalTests - passedTests;
        const totalTime = this.endTime - this.startTime;
        const avgResponseTime = this.results.reduce((sum, r) => sum + r.responseTime, 0) / totalTests;

        console.log('\n📊 API Connection Test Report');
        console.log('='.repeat(50));
        console.log(`Total Tests: ${totalTests}`);
        console.log(`Passed: ${passedTests} ✅`);
        console.log(`Failed: ${failedTests} ❌`);
        console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
        console.log(`Total Time: ${totalTime}ms`);
        console.log(`Average Response Time: ${avgResponseTime.toFixed(0)}ms`);

        // Group results by category
        const categories = {};
        this.results.forEach(result => {
            if (!categories[result.category]) {
                categories[result.category] = [];
            }
            categories[result.category].push(result);
        });

        console.log('\n📈 Results by Category:');
        Object.entries(categories).forEach(([category, results]) => {
            const passed = results.filter(r => r.success).length;
            const total = results.length;
            const rate = ((passed / total) * 100).toFixed(1);
            console.log(`${category}: ${passed}/${total} (${rate}%)`);
        });

        // Show failed tests
        const failedTests = this.results.filter(r => !r.success);
        if (failedTests.length > 0) {
            console.log('\n❌ Failed Tests:');
            failedTests.forEach(test => {
                console.log(`  - ${test.name}: ${test.error}`);
            });
        }

        // Show slow tests
        const slowTests = this.results.filter(r => r.responseTime > 1000);
        if (slowTests.length > 0) {
            console.log('\n🐌 Slow Tests (>1s):');
            slowTests.forEach(test => {
                console.log(`  - ${test.name}: ${test.responseTime}ms`);
            });
        }

        this.displayResultsInUI();
    }

    /**
     * Display results in the UI
     */
    displayResultsInUI() {
        const container = document.getElementById('apiTestResults');
        if (!container) {
            console.warn('No #apiTestResults container found');
            return;
        }

        const totalTests = this.results.length;
        const passedTests = this.results.filter(r => r.success).length;
        const failedTests = totalTests - passedTests;
        const successRate = ((passedTests / totalTests) * 100).toFixed(1);

        container.innerHTML = `
            <div class="test-report">
                <h3>API Connection Test Results</h3>
                <div class="test-summary">
                    <div class="test-stat">
                        <span class="stat-label">Total Tests:</span>
                        <span class="stat-value">${totalTests}</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Passed:</span>
                        <span class="stat-value success">${passedTests} ✅</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Failed:</span>
                        <span class="stat-value error">${failedTests} ❌</span>
                    </div>
                    <div class="test-stat">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">${successRate}%</span>
                    </div>
                </div>
                
                <div class="test-details">
                    <h4>Test Details:</h4>
                    <div class="test-list">
                        ${this.results.map(result => `
                            <div class="test-item ${result.success ? 'success' : 'error'}">
                                <span class="test-name">${result.name}</span>
                                <span class="test-status">${result.success ? 'PASS' : 'FAIL'}</span>
                                <span class="test-time">${result.responseTime}ms</span>
                                ${result.error ? `<span class="test-error">${result.error}</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Test specific endpoint patterns
     */
    async testEndpointPatterns() {
        console.log('\n🔍 Testing Endpoint Patterns...');

        const patterns = [
            // Test the broken endpoints that frontend is trying to call
            { name: 'Frontend Dashboard Summary (BROKEN)', url: '/api/dashboard-summary', expected: false },
            { name: 'Frontend Charts Data (BROKEN)', url: '/api/charts-data', expected: false },
            { name: 'Frontend AI Suggestions (BROKEN)', url: '/api/ai-suggestions', expected: false },
            { name: 'Frontend Train AI (BROKEN)', url: '/api/train-ai', expected: false },
            { name: 'Frontend Scrape Trigger (BROKEN)', url: '/api/scrape-trigger', expected: false },

            // Test the correct endpoints
            { name: 'Backend Dashboard Summary (CORRECT)', url: '/api/dashboard/summary', expected: true },
            { name: 'Backend Charts Data (CORRECT)', url: '/api/dashboard/charts-data', expected: true },
            { name: 'Backend AI Suggestions (CORRECT)', url: '/api/dashboard/ai-suggestions', expected: true },
            { name: 'Backend AI Feedback (CORRECT)', url: '/api/dashboard/ai-feedback', expected: true },
            { name: 'Backend Scrape (CORRECT)', url: '/api/scraping/scrape', expected: true }
        ];

        for (const pattern of patterns) {
            try {
                const response = await fetch(pattern.url);
                const actual = response.ok;
                const status = actual === pattern.expected ? '✅' : '❌';
                console.log(`${status} ${pattern.name}: ${actual ? 'EXISTS' : 'MISSING'} (Expected: ${pattern.expected ? 'EXISTS' : 'MISSING'})`);
            } catch (error) {
                const status = pattern.expected ? '❌' : '✅';
                console.log(`${status} ${pattern.name}: MISSING (Expected: ${pattern.expected ? 'EXISTS' : 'MISSING'})`);
            }
        }
    }

    /**
     * Test file upload functionality
     */
    async testFileUpload() {
        console.log('\n📁 Testing File Upload...');

        // Create a test file
        const testFile = new File(['Test PDF content'], 'test.pdf', { type: 'application/pdf' });
        const formData = new FormData();
        formData.append('file', testFile);
        formData.append('title', 'Test Document');
        formData.append('source', 'Test');
        formData.append('category', 'Test');

        try {
            const response = await fetch('/api/ocr/process-and-save', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                console.log('✅ File upload endpoint is accessible');
                const result = await response.json();
                console.log('📄 Upload response:', result);
            } else {
                console.log('❌ File upload failed:', response.status, response.statusText);
            }
        } catch (error) {
            console.log('❌ File upload error:', error.message);
        }
    }

    /**
     * Utility function for delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global instance
window.apiTester = new APIConnectionTester();

// Auto-run tests when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 API Connection Tester loaded');

    // Add test button if not exists
    if (!document.getElementById('runAPITests')) {
        const testButton = document.createElement('button');
        testButton.id = 'runAPITests';
        testButton.textContent = 'Run API Tests';
        testButton.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10000;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        `;
        testButton.onclick = () => {
            window.apiTester.runAllTests();
        };
        document.body.appendChild(testButton);
    }

    // Add results container if not exists
    if (!document.getElementById('apiTestResults')) {
        const resultsContainer = document.createElement('div');
        resultsContainer.id = 'apiTestResults';
        resultsContainer.style.cssText = `
            position: fixed;
            top: 60px;
            right: 10px;
            width: 400px;
            max-height: 500px;
            overflow-y: auto;
            background: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 15px;
            z-index: 10000;
            display: none;
        `;
        document.body.appendChild(resultsContainer);
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIConnectionTester;
} 