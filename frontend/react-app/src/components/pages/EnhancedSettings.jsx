import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSystemContext } from '../../contexts/SystemContext'

const EnhancedSettings = () => {
  const { settings, updateSettings } = useSystemContext()
  const [localSettings, setLocalSettings] = useState(settings)
  const [activeTab, setActiveTab] = useState('general')

  const handleSave = () => {
    updateSettings(localSettings)
    // Show success message
    alert('تنظیمات با موفقیت ذخیره شد')
  }

  const handleReset = () => {
    setLocalSettings(settings)
  }

  const tabs = [
    { id: 'general', name: 'عمومی', icon: '⚙️' },
    { id: 'notifications', name: 'اعلان‌ها', icon: '🔔' },
    { id: 'security', name: 'امنیت', icon: '🔒' },
    { id: 'advanced', name: 'پیشرفته', icon: '🔧' }
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">تنظیمات سیستم</h1>
        <p className="text-gray-600 mt-2">تنظیم و پیکربندی سیستم آرشیو اسناد</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">دسته‌بندی تنظیمات</h2>
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-right px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border-r-4 border-blue-500'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="ml-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3"
        >
          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === 'general' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">تنظیمات عمومی</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      زبان سیستم
                    </label>
                    <select
                      value={localSettings.language}
                      onChange={(e) => setLocalSettings({...localSettings, language: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="fa">فارسی</option>
                      <option value="en">English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      تم سیستم
                    </label>
                    <select
                      value={localSettings.theme}
                      onChange={(e) => setLocalSettings({...localSettings, theme: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="light">روشن</option>
                      <option value="dark">تیره</option>
                      <option value="auto">خودکار</option>
                    </select>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={localSettings.notifications}
                        onChange={(e) => setLocalSettings({...localSettings, notifications: e.target.checked})}
                        className="ml-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">فعال‌سازی اعلان‌ها</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">تنظیمات اعلان‌ها</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h3 className="font-medium text-gray-900">اعلان‌های سیستم</h3>
                      <p className="text-sm text-gray-500">اطلاع‌رسانی درباره وضعیت سیستم</p>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h3 className="font-medium text-gray-900">اعلان‌های پردازش</h3>
                      <p className="text-sm text-gray-500">اطلاع‌رسانی درباره تکمیل پردازش اسناد</p>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <h3 className="font-medium text-gray-900">اعلان‌های ایمیل</h3>
                      <p className="text-sm text-gray-500">ارسال اعلان‌ها از طریق ایمیل</p>
                    </div>
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">تنظیمات امنیت</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      مدت زمان جلسه (دقیقه)
                    </label>
                    <input
                      type="number"
                      defaultValue="30"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="ml-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">فعال‌سازی احراز هویت دو مرحله‌ای</span>
                    </label>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="ml-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">رمزگذاری فایل‌های آپلود شده</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'advanced' && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">تنظیمات پیشرفته</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      حداکثر اندازه فایل (MB)
                    </label>
                    <input
                      type="number"
                      defaultValue="100"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      تعداد همزمان پردازش
                    </label>
                    <input
                      type="number"
                      defaultValue="3"
                      min="1"
                      max="10"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      آدرس API سرور
                    </label>
                    <input
                      type="text"
                      defaultValue="http://localhost:8000"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="flex items-center justify-end space-x-4 space-x-reverse mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={handleReset}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                بازنشانی
              </button>
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                ذخیره تنظیمات
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default EnhancedSettings