// API Service for Iranian Legal Archive System
import { apiClient, API_CONFIG } from '../config/api.js'

class ApiService {
  // System Status
  async getSystemStatus() {
    try {
      return await apiClient.get(API_CONFIG.ENDPOINTS.SYSTEM_STATUS)
    } catch (error) {
      console.error('Failed to get system status:', error)
      throw error
    }
  }

  // Documents
  async getDocuments(params = {}) {
    try {
      return await apiClient.get(API_CONFIG.ENDPOINTS.DOCUMENTS, params)
    } catch (error) {
      console.error('Failed to get documents:', error)
      throw error
    }
  }

  async searchDocuments(query, filters = {}) {
    try {
      return await apiClient.post(API_CONFIG.ENDPOINTS.DOCUMENT_SEARCH, {
        query,
        filters
      })
    } catch (error) {
      console.error('Failed to search documents:', error)
      throw error
    }
  }

  async uploadDocument(file, onProgress = null) {
    try {
      return await apiClient.uploadFile(
        API_CONFIG.ENDPOINTS.DOCUMENT_UPLOAD,
        file,
        onProgress
      )
    } catch (error) {
      console.error('Failed to upload document:', error)
      throw error
    }
  }

  // AI Analysis
  async analyzeDocument(documentId) {
    try {
      return await apiClient.post(API_CONFIG.ENDPOINTS.AI_ANALYSIS, {
        document_id: documentId
      })
    } catch (error) {
      console.error('Failed to analyze document:', error)
      throw error
    }
  }

  async getDocumentSummary(documentId) {
    try {
      return await apiClient.post(API_CONFIG.ENDPOINTS.AI_SUMMARY, {
        document_id: documentId
      })
    } catch (error) {
      console.error('Failed to get document summary:', error)
      throw error
    }
  }

  // Proxy Management
  async getProxies() {
    try {
      return await apiClient.get(API_CONFIG.ENDPOINTS.PROXIES)
    } catch (error) {
      console.error('Failed to get proxies:', error)
      throw error
    }
  }

  async addProxy(proxyData) {
    try {
      return await apiClient.post(API_CONFIG.ENDPOINTS.PROXIES, proxyData)
    } catch (error) {
      console.error('Failed to add proxy:', error)
      throw error
    }
  }

  async testProxy(proxyId) {
    try {
      return await apiClient.post(API_CONFIG.ENDPOINTS.PROXY_TEST, {
        proxy_id: proxyId
      })
    } catch (error) {
      console.error('Failed to test proxy:', error)
      throw error
    }
  }

  async deleteProxy(proxyId) {
    try {
      return await apiClient.delete(`${API_CONFIG.ENDPOINTS.PROXIES}/${proxyId}`)
    } catch (error) {
      console.error('Failed to delete proxy:', error)
      throw error
    }
  }

  // Settings
  async getSettings() {
    try {
      return await apiClient.get(API_CONFIG.ENDPOINTS.SETTINGS)
    } catch (error) {
      console.error('Failed to get settings:', error)
      throw error
    }
  }

  async updateSettings(settings) {
    try {
      return await apiClient.put(API_CONFIG.ENDPOINTS.SETTINGS, settings)
    } catch (error) {
      console.error('Failed to update settings:', error)
      throw error
    }
  }

  // System Statistics
  async getSystemStats() {
    try {
      return await apiClient.get(API_CONFIG.ENDPOINTS.SYSTEM_STATS)
    } catch (error) {
      console.error('Failed to get system stats:', error)
      throw error
    }
  }
}

// Create singleton instance
const apiService = new ApiService()

export default apiService