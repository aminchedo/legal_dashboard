# Iranian Legal Archive System - Customization Guide

## 🎨 Quick Customizations

### 1. Change Application Title
Edit `src/index.html`:
```html
<title>Your Custom Title</title>
```

### 2. Modify Sidebar Menu
Edit `src/components/layout/EnhancedSidebar.jsx`:
```jsx
const menuItems = [
  { path: '/', name: 'داشبورد', icon: '📊', description: 'نمای کلی سیستم' },
  { path: '/search', name: 'جستجو', icon: '🔍', description: 'جستجو در اسناد' },
  // Add your custom menu items here
  { path: '/custom', name: 'صفحه سفارشی', icon: '⭐', description: 'توضیحات' },
]
```

### 3. Update Dashboard Statistics
Edit `src/components/pages/EnhancedDashboard.jsx`:
```jsx
const [stats, setStats] = useState({
  totalDocuments: 0,
  processedToday: 0,
  pendingAnalysis: 0,
  systemHealth: 100,
  // Add your custom stats
  customMetric: 0
})
```

### 4. Customize Colors
Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: {
        50: '#your-color-50',
        500: '#your-color-500',
        600: '#your-color-600',
      }
    }
  }
}
```

### 5. Add New Page
1. Create new component in `src/components/pages/`
2. Add route in `src/App.jsx`:
```jsx
<Route path="/new-page" element={<NewPageComponent />} />
```
3. Add menu item in `EnhancedSidebar.jsx`

### 6. Modify API Endpoints
Edit `src/config/api.js`:
```js
ENDPOINTS: {
  // Add your custom endpoints
  CUSTOM_ENDPOINT: '/api/custom',
}
```

## 🔧 Advanced Customizations

### State Management
- Edit `src/contexts/SystemContext.jsx` for global state
- Add new context providers as needed

### Styling
- Modify `src/index.css` for global styles
- Update `src/App.css` for app-specific styles
- Use Tailwind classes for component styling

### API Integration
- Extend `src/services/apiService.js` for new API calls
- Update `src/config/api.js` for new endpoints

## 📱 Responsive Design
The app is built with Tailwind CSS and is fully responsive:
- Mobile-first design
- Breakpoints: sm, md, lg, xl
- RTL support for Persian text

## 🌐 Internationalization
To add English support:
1. Create language files
2. Add language switcher component
3. Update text content conditionally

## 🚀 Performance Optimization
- Components are lazy-loaded
- Images are optimized
- Code splitting is configured
- Gzip compression enabled

---

**Happy Customizing! 🎉**