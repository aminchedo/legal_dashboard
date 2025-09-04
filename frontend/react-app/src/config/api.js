// API Configuration for Iranian Legal Archive System
const API_CONFIG = {
  // Base API URL - will be automatically detected in production
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API Endpoints
  ENDPOINTS: {
    // Authentication
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    
    // Documents
    DOCUMENTS: '/api/documents',
    DOCUMENT_UPLOAD: '/api/documents/upload',
    DOCUMENT_SEARCH: '/api/documents/search',
    DOCUMENT_ANALYZE: '/api/documents/analyze',
    
    // AI Analysis
    AI_ANALYSIS: '/api/ai/analyze',
    AI_SUMMARY: '/api/ai/summary',
    AI_KEYWORDS: '/api/ai/keywords',
    
    // Proxy Management
    PROXIES: '/api/proxies',
    PROXY_TEST: '/api/proxies/test',
    
    // System
    SYSTEM_STATUS: '/api/system/status',
    SYSTEM_HEALTH: '/api/system/health',
    SYSTEM_STATS: '/api/system/stats',
    
    // Settings
    SETTINGS: '/api/settings',
    USER_SETTINGS: '/api/settings/user',
  },
  
  // WebSocket Configuration
  WEBSOCKET: {
    URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
    RECONNECT_INTERVAL: 5000,
    MAX_RECONNECT_ATTEMPTS: 5,
  },
  
  // Request Configuration
  REQUEST: {
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
  },
  
  // File Upload Configuration
  UPLOAD: {
    MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
    ALLOWED_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'],
    CHUNK_SIZE: 1024 * 1024, // 1MB chunks
  }
}

// API Client Class
class ApiClient {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL
    this.timeout = API_CONFIG.REQUEST.TIMEOUT
  }

  // Get full URL for endpoint
  getUrl(endpoint) {
    return `${this.baseURL}${endpoint}`
  }

  // Make HTTP request
  async request(endpoint, options = {}) {
    const url = this.getUrl(endpoint)
    const config = {
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // Add authentication token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      
      return await response.text()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // GET request
  async get(endpoint, params = {}) {
    const url = new URL(this.getUrl(endpoint))
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
    
    return this.request(url.toString(), { method: 'GET' })
  }

  // POST request
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // PUT request
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }

  // File upload
  async uploadFile(endpoint, file, onProgress = null) {
    const formData = new FormData()
    formData.append('file', file)

    const xhr = new XMLHttpRequest()
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = (e.loaded / e.total) * 100
          onProgress(percentComplete)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (error) {
            resolve(xhr.responseText)
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'))
      })

      const token = localStorage.getItem('auth_token')
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      }

      xhr.open('POST', this.getUrl(endpoint))
      xhr.send(formData)
    })
  }
}

// Create singleton instance
const apiClient = new ApiClient()

// Export configuration and client
export { API_CONFIG, apiClient }
export default apiClient