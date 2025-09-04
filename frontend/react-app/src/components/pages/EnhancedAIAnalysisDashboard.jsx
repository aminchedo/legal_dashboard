import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSystemContext } from '../../contexts/SystemContext'

const EnhancedAIAnalysisDashboard = () => {
  const { setLoading } = useSystemContext()
  const [analysisResults, setAnalysisResults] = useState([])
  const [selectedDocument, setSelectedDocument] = useState(null)

  const handleAnalysis = async (documentId) => {
    setLoading(true)
    try {
      // Simulate AI analysis
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockResult = {
        id: documentId,
        summary: 'خلاصه تحلیل هوش مصنوعی: این سند شامل احکام حقوقی مهمی است که نیاز به بررسی دقیق دارد.',
        keywords: ['حقوق مدنی', 'قرارداد', 'مسئولیت', 'خسارت'],
        sentiment: 'neutral',
        confidence: 0.87,
        recommendations: [
          'بررسی دقیق‌تر مفاد قرارداد',
          'مشاوره با متخصص حقوقی',
          'بررسی رویه‌های قضایی مشابه'
        ]
      }
      
      setAnalysisResults(prev => [...prev, mockResult])
    } catch (error) {
      console.error('Analysis error:', error)
    } finally {
      setLoading(false)
    }
  }

  const mockDocuments = [
    { id: 1, title: 'قانون مدنی ایران', status: 'pending' },
    { id: 2, title: 'آیین‌نامه اجرایی قانون کار', status: 'analyzed' },
    { id: 3, title: 'بخشنامه مالیاتی', status: 'pending' }
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">تحلیل هوش مصنوعی</h1>
        <p className="text-gray-600 mt-2">تحلیل و پردازش اسناد با استفاده از هوش مصنوعی</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">اسناد در انتظار تحلیل</h2>
          <div className="space-y-3">
            {mockDocuments.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">{doc.title}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    doc.status === 'analyzed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {doc.status === 'analyzed' ? 'تحلیل شده' : 'در انتظار'}
                  </span>
                </div>
                {doc.status === 'pending' && (
                  <button
                    onClick={() => handleAnalysis(doc.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    شروع تحلیل
                  </button>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">نتایج تحلیل</h2>
          {analysisResults.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🤖</div>
              <p>هنوز تحلیلی انجام نشده است</p>
            </div>
          ) : (
            <div className="space-y-4">
              {analysisResults.map((result) => (
                <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">نتیجه تحلیل</h3>
                    <span className="text-sm text-gray-500">
                      اطمینان: {(result.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{result.summary}</p>
                  
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">کلمات کلیدی:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.keywords.map((keyword, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">توصیه‌ها:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {result.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-blue-500 ml-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default EnhancedAIAnalysisDashboard