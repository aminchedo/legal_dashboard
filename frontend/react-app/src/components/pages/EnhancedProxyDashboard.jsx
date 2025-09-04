import React, { useState } from 'react'
import { motion } from 'framer-motion'

const EnhancedProxyDashboard = () => {
  const [proxies, setProxies] = useState([
    { id: 1, name: 'پروکسی اصلی', host: 'proxy1.example.com', port: 8080, status: 'active', speed: 'fast' },
    { id: 2, name: 'پروکسی پشتیبان', host: 'proxy2.example.com', port: 8080, status: 'inactive', speed: 'medium' },
    { id: 3, name: 'پروکسی محلی', host: '127.0.0.1', port: 3128, status: 'active', speed: 'fast' }
  ])

  const [newProxy, setNewProxy] = useState({
    name: '',
    host: '',
    port: '',
    username: '',
    password: ''
  })

  const addProxy = () => {
    if (newProxy.name && newProxy.host && newProxy.port) {
      const proxy = {
        id: Date.now(),
        ...newProxy,
        status: 'inactive',
        speed: 'unknown'
      }
      setProxies([...proxies, proxy])
      setNewProxy({ name: '', host: '', port: '', username: '', password: '' })
    }
  }

  const toggleProxy = (id) => {
    setProxies(proxies.map(proxy => 
      proxy.id === id 
        ? { ...proxy, status: proxy.status === 'active' ? 'inactive' : 'active' }
        : proxy
    ))
  }

  const deleteProxy = (id) => {
    setProxies(proxies.filter(proxy => proxy.id !== id))
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900">مدیریت پروکسی</h1>
        <p className="text-gray-600 mt-2">تنظیم و مدیریت پروکسی‌های سیستم</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">افزودن پروکسی جدید</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نام پروکسی
              </label>
              <input
                type="text"
                value={newProxy.name}
                onChange={(e) => setNewProxy({...newProxy, name: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="نام پروکسی"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  آدرس
                </label>
                <input
                  type="text"
                  value={newProxy.host}
                  onChange={(e) => setNewProxy({...newProxy, host: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="host.example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  پورت
                </label>
                <input
                  type="number"
                  value={newProxy.port}
                  onChange={(e) => setNewProxy({...newProxy, port: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="8080"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  نام کاربری
                </label>
                <input
                  type="text"
                  value={newProxy.username}
                  onChange={(e) => setNewProxy({...newProxy, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="اختیاری"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  رمز عبور
                </label>
                <input
                  type="password"
                  value={newProxy.password}
                  onChange={(e) => setNewProxy({...newProxy, password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="اختیاری"
                />
              </div>
            </div>

            <button
              onClick={addProxy}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              افزودن پروکسی
            </button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">لیست پروکسی‌ها</h2>
          <div className="space-y-3">
            {proxies.map((proxy) => (
              <div key={proxy.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{proxy.name}</h3>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <span className={`w-2 h-2 rounded-full ${
                      proxy.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                    }`}></span>
                    <span className="text-sm text-gray-500">
                      {proxy.status === 'active' ? 'فعال' : 'غیرفعال'}
                    </span>
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 mb-3">
                  {proxy.host}:{proxy.port}
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    سرعت: {proxy.speed === 'fast' ? 'سریع' : proxy.speed === 'medium' ? 'متوسط' : 'نامشخص'}
                  </span>
                  
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <button
                      onClick={() => toggleProxy(proxy.id)}
                      className={`px-3 py-1 text-xs rounded-full ${
                        proxy.status === 'active' 
                          ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {proxy.status === 'active' ? 'غیرفعال' : 'فعال'}
                    </button>
                    <button
                      onClick={() => deleteProxy(proxy.id)}
                      className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full hover:bg-red-200"
                    >
                      حذف
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default EnhancedProxyDashboard