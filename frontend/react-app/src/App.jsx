import React from 'react'
import { HashRouter as Router, Routes, Route } from 'react-router-dom'
import { SystemContextProvider } from './contexts/SystemContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import Header from './components/layout/Header'
import EnhancedSidebar from './components/layout/EnhancedSidebar'
import EnhancedDashboard from './components/pages/EnhancedDashboard'
import EnhancedSearchInterface from './components/pages/EnhancedSearchInterface'
import EnhancedAIAnalysisDashboard from './components/pages/EnhancedAIAnalysisDashboard'
import EnhancedProxyDashboard from './components/pages/EnhancedProxyDashboard'
import EnhancedDocumentProcessing from './components/pages/EnhancedDocumentProcessing'
import EnhancedSettings from './components/pages/EnhancedSettings'
import './App.css'

function App() {
  return (
    <SystemContextProvider>
      <WebSocketProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 rtl">
            <Header />
            <div className="flex">
              <EnhancedSidebar />
              <main className="flex-1 p-6">
                <Routes>
                  <Route path="/" element={<EnhancedDashboard />} />
                  <Route path="/search" element={<EnhancedSearchInterface />} />
                  <Route path="/ai-analysis" element={<EnhancedAIAnalysisDashboard />} />
                  <Route path="/proxy" element={<EnhancedProxyDashboard />} />
                  <Route path="/processing" element={<EnhancedDocumentProcessing />} />
                  <Route path="/settings" element={<EnhancedSettings />} />
                </Routes>
              </main>
            </div>
          </div>
        </Router>
      </WebSocketProvider>
    </SystemContextProvider>
  )
}

export default App