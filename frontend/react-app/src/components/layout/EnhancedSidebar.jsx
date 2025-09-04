import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'

const EnhancedSidebar = () => {
  const location = useLocation()
  
  const menuItems = [
    { path: '/', name: 'داشبورد', icon: '📊', description: 'نمای کلی سیستم' },
    { path: '/search', name: 'جستجو', icon: '🔍', description: 'جستجو در اسناد' },
    { path: '/ai-analysis', name: 'تحلیل هوش مصنوعی', icon: '🤖', description: 'تحلیل اسناد با AI' },
    { path: '/proxy', name: 'مدیریت پروکسی', icon: '🌐', description: 'تنظیمات پروکسی' },
    { path: '/processing', name: 'پردازش اسناد', icon: '📄', description: 'پردازش و تحلیل' },
    { path: '/settings', name: 'تنظیمات', icon: '⚙️', description: 'تنظیمات سیستم' },
  ]

  return (
    <aside className="w-64 bg-white shadow-lg border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-6">
          منوی اصلی
        </h2>
      </div>
      
      <nav className="mt-6">
        {menuItems.map((item, index) => (
          <motion.div
            key={item.path}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Link
              to={item.path}
              className={`block px-6 py-4 text-right hover:bg-gray-50 border-r-4 transition-all duration-200 group ${
                location.pathname === item.path
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-transparent text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 space-x-reverse">
                  <span className="text-xl">{item.icon}</span>
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500 group-hover:text-gray-700">
                      {item.description}
                    </div>
                  </div>
                </div>
                
                {location.pathname === item.path && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-2 h-2 bg-blue-500 rounded-full"
                  />
                )}
              </div>
            </Link>
          </motion.div>
        ))}
      </nav>
      
      <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          سیستم آرشیو اسناد حقوقی ایران
          <br />
          تمامی حقوق محفوظ است
        </div>
      </div>
    </aside>
  )
}

export default EnhancedSidebar