import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useSystemContext } from '../../contexts/SystemContext'
import { useWebSocket } from '../../contexts/WebSocketContext'

const EnhancedDashboard = () => {
  const { documents, loading, error } = useSystemContext()
  const { isConnected, lastMessage } = useWebSocket()
  const [stats, setStats] = useState({
    totalDocuments: 0,
    processedToday: 0,
    pendingAnalysis: 0,
    systemHealth: 100
  })

  useEffect(() => {
    // Simulate loading stats
    setStats({
      totalDocuments: documents.length || 1247,
      processedToday: 23,
      pendingAnalysis: 5,
      systemHealth: isConnected ? 100 : 85
    })
  }, [documents, isConnected])

  const StatCard = ({ title, value, icon, color, trend }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${color}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className="text-xs text-green-600 mt-1">{trend}</p>
          )}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </motion.div>
  )

  const RecentActivity = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white rounded-lg shadow-md p-6"
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-4">فعالیت‌های اخیر</h3>
      <div className="space-y-3">
        {[
          { action: 'سند جدید پردازش شد', time: '2 دقیقه پیش', type: 'success' },
          { action: 'تحلیل AI تکمیل شد', time: '5 دقیقه پیش', type: 'info' },
          { action: 'جستجوی جدید انجام شد', time: '10 دقیقه پیش', type: 'search' },
          { action: 'پشتیبان‌گیری انجام شد', time: '1 ساعت پیش', type: 'backup' }
        ].map((activity, index) => (
          <div key={index} className="flex items-center space-x-3 space-x-reverse">
            <div className={`w-2 h-2 rounded-full ${
              activity.type === 'success' ? 'bg-green-500' :
              activity.type === 'info' ? 'bg-blue-500' :
              activity.type === 'search' ? 'bg-yellow-500' : 'bg-purple-500'
            }`}></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">{activity.action}</p>
              <p className="text-xs text-gray-500">{activity.time}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-800">خطا در بارگذاری داشبورد</h3>
        <p className="text-red-600 mt-2">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">داشبورد سیستم</h1>
        <p className="text-gray-600 mt-2">نمای کلی از وضعیت سیستم آرشیو اسناد حقوقی</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="کل اسناد"
          value={stats.totalDocuments.toLocaleString('fa-IR')}
          icon="📄"
          color="border-blue-500"
          trend="+12 این هفته"
        />
        <StatCard
          title="پردازش امروز"
          value={stats.processedToday}
          icon="⚡"
          color="border-green-500"
          trend="+5 از دیروز"
        />
        <StatCard
          title="در انتظار تحلیل"
          value={stats.pendingAnalysis}
          icon="⏳"
          color="border-yellow-500"
        />
        <StatCard
          title="سلامت سیستم"
          value={`${stats.systemHealth}%`}
          icon="💚"
          color="border-green-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">وضعیت اتصال</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">اتصال WebSocket</span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {isConnected ? 'متصل' : 'قطع'}
              </span>
            </div>
            {lastMessage && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">آخرین پیام:</p>
                <p className="text-sm text-gray-900">{JSON.stringify(lastMessage, null, 2)}</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default EnhancedDashboard