import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSystemContext } from '../../contexts/SystemContext'

const EnhancedSearchInterface = () => {
  const { searchResults, setSearchResults, setLoading } = useSystemContext()
  const [searchQuery, setSearchQuery] = useState('')
  const [searchFilters, setSearchFilters] = useState({
    documentType: '',
    dateRange: '',
    category: ''
  })

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Mock search results
      const mockResults = [
        {
          id: 1,
          title: 'قانون مدنی ایران',
          type: 'قانون',
          date: '1399/01/15',
          summary: 'قانون مدنی جمهوری اسلامی ایران شامل احکام حقوقی...'
        },
        {
          id: 2,
          title: 'آیین‌نامه اجرایی قانون کار',
          type: 'آیین‌نامه',
          date: '1398/12/20',
          summary: 'آیین‌نامه اجرایی قانون کار و مقررات مربوطه...'
        }
      ]
      
      setSearchResults(mockResults)
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">جستجو در اسناد</h1>
        <p className="text-gray-600 mt-2">جستجوی پیشرفته در آرشیو اسناد حقوقی</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-md p-6"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              عبارت جستجو
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="کلمات کلیدی، عنوان سند، یا محتوای مورد نظر..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نوع سند
              </label>
              <select
                value={searchFilters.documentType}
                onChange={(e) => setSearchFilters({...searchFilters, documentType: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه انواع</option>
                <option value="law">قانون</option>
                <option value="regulation">آیین‌نامه</option>
                <option value="circular">بخشنامه</option>
                <option value="judgment">رای</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                بازه زمانی
              </label>
              <select
                value={searchFilters.dateRange}
                onChange={(e) => setSearchFilters({...searchFilters, dateRange: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه زمان‌ها</option>
                <option value="last-week">هفته گذشته</option>
                <option value="last-month">ماه گذشته</option>
                <option value="last-year">سال گذشته</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                دسته‌بندی
              </label>
              <select
                value={searchFilters.category}
                onChange={(e) => setSearchFilters({...searchFilters, category: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه دسته‌ها</option>
                <option value="civil">حقوق مدنی</option>
                <option value="criminal">حقوق جزا</option>
                <option value="commercial">حقوق تجارت</option>
                <option value="labor">حقوق کار</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleSearch}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            جستجو
          </button>
        </div>
      </motion.div>

      {searchResults.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <h2 className="text-xl font-semibold text-gray-900">
            نتایج جستجو ({searchResults.length})
          </h2>
          
          {searchResults.map((result) => (
            <motion.div
              key={result.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {result.title}
                  </h3>
                  <p className="text-gray-600 mb-3">{result.summary}</p>
                  <div className="flex items-center space-x-4 space-x-reverse text-sm text-gray-500">
                    <span>نوع: {result.type}</span>
                    <span>تاریخ: {result.date}</span>
                  </div>
                </div>
                <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                  مشاهده کامل
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  )
}

export default EnhancedSearchInterface