import React from 'react'
import { useSystemContext } from '../../contexts/SystemContext'
import { useWebSocket } from '../../contexts/WebSocketContext'

const Header = () => {
  const { isOnline, systemStatus } = useSystemContext()
  const { connectionStatus } = useWebSocket()

  const getStatusColor = () => {
    if (!isOnline) return 'text-red-500'
    if (connectionStatus === 'connected') return 'text-green-500'
    if (connectionStatus === 'error') return 'text-red-500'
    return 'text-yellow-500'
  }

  const getStatusText = () => {
    if (!isOnline) return 'آفلاین'
    if (connectionStatus === 'connected') return 'آنلاین'
    if (connectionStatus === 'error') return 'خطا در اتصال'
    return 'در حال اتصال...'
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 space-x-reverse">
          <h1 className="text-2xl font-bold text-gray-900">
            سیستم آرشیو اسناد حقوقی ایران
          </h1>
          <div className="text-sm text-gray-500">
            نسخه 1.0.0
          </div>
        </div>
        
        <div className="flex items-center space-x-4 space-x-reverse">
          <div className="flex items-center space-x-2 space-x-reverse">
            <div className={`w-2 h-2 rounded-full ${getStatusColor().replace('text-', 'bg-')}`}></div>
            <span className={`text-sm font-medium ${getStatusColor()}`}>
              {getStatusText()}
            </span>
          </div>
          
          <div className="text-sm text-gray-500">
            وضعیت سیستم: {systemStatus === 'operational' ? 'عملیاتی' : 'غیرعملیاتی'}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header