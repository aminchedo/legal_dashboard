import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSystemContext } from '../../contexts/SystemContext'

const EnhancedDocumentProcessing = () => {
  const { setLoading } = useSystemContext()
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [processingQueue, setProcessingQueue] = useState([])
  const [dragActive, setDragActive] = useState(false)

  const handleFileUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploaded',
      progress: 0
    }))
    
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files)
    }
  }

  const processDocument = async (fileId) => {
    setLoading(true)
    
    // Move to processing queue
    const file = uploadedFiles.find(f => f.id === fileId)
    if (file) {
      setProcessingQueue(prev => [...prev, { ...file, status: 'processing' }])
      setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
    }

    try {
      // Simulate processing
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 200))
        setProcessingQueue(prev => 
          prev.map(f => f.id === fileId ? { ...f, progress } : f)
        )
      }

      // Move to completed
      setProcessingQueue(prev => 
        prev.map(f => f.id === fileId ? { ...f, status: 'completed' } : f)
      )
    } catch (error) {
      console.error('Processing error:', error)
      setProcessingQueue(prev => 
        prev.map(f => f.id === fileId ? { ...f, status: 'error' } : f)
      )
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">پردازش اسناد</h1>
        <p className="text-gray-600 mt-2">آپلود و پردازش اسناد حقوقی</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">آپلود اسناد</h2>
          
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-4xl mb-4">📄</div>
            <p className="text-gray-600 mb-4">
              فایل‌های خود را اینجا بکشید یا کلیک کنید
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={(e) => handleFileUpload(e.target.files)}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
            >
              انتخاب فایل
            </label>
            <p className="text-xs text-gray-500 mt-2">
              فرمت‌های پشتیبانی شده: PDF, DOC, DOCX, TXT
            </p>
          </div>

          {uploadedFiles.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">فایل‌های آپلود شده</h3>
              <div className="space-y-2">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 space-x-reverse">
                      <div className="text-2xl">📄</div>
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => processDocument(file.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      پردازش
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">صف پردازش</h2>
          
          {processingQueue.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">⚙️</div>
              <p>هیچ سندی در حال پردازش نیست</p>
            </div>
          ) : (
            <div className="space-y-4">
              {processingQueue.map((file) => (
                <div key={file.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{file.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      file.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      file.status === 'completed' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {file.status === 'processing' ? 'در حال پردازش' :
                       file.status === 'completed' ? 'تکمیل شده' : 'خطا'}
                    </span>
                  </div>
                  
                  {file.status === 'processing' && (
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      ></div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{formatFileSize(file.size)}</span>
                    {file.status === 'processing' && (
                      <span>{file.progress}%</span>
                    )}
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

export default EnhancedDocumentProcessing