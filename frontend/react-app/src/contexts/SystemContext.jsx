import React, { createContext, useContext, useReducer, useEffect } from 'react'

const SystemContext = createContext()

const initialState = {
  isOnline: true,
  systemStatus: 'operational',
  user: null,
  settings: {
    language: 'fa',
    theme: 'light',
    notifications: true
  },
  documents: [],
  searchResults: [],
  loading: false,
  error: null
}

const systemReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false }
    case 'SET_ONLINE_STATUS':
      return { ...state, isOnline: action.payload }
    case 'SET_SYSTEM_STATUS':
      return { ...state, systemStatus: action.payload }
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'SET_DOCUMENTS':
      return { ...state, documents: action.payload }
    case 'SET_SEARCH_RESULTS':
      return { ...state, searchResults: action.payload }
    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    default:
      return state
  }
}

export const SystemContextProvider = ({ children }) => {
  const [state, dispatch] = useReducer(systemReducer, initialState)

  useEffect(() => {
    // Check online status
    const handleOnline = () => dispatch({ type: 'SET_ONLINE_STATUS', payload: true })
    const handleOffline = () => dispatch({ type: 'SET_ONLINE_STATUS', payload: false })

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const value = {
    ...state,
    dispatch,
    setLoading: (loading) => dispatch({ type: 'SET_LOADING', payload: loading }),
    setError: (error) => dispatch({ type: 'SET_ERROR', payload: error }),
    setUser: (user) => dispatch({ type: 'SET_USER', payload: user }),
    setDocuments: (documents) => dispatch({ type: 'SET_DOCUMENTS', payload: documents }),
    setSearchResults: (results) => dispatch({ type: 'SET_SEARCH_RESULTS', payload: results }),
    updateSettings: (settings) => dispatch({ type: 'UPDATE_SETTINGS', payload: settings }),
    clearError: () => dispatch({ type: 'CLEAR_ERROR' })
  }

  return (
    <SystemContext.Provider value={value}>
      {children}
    </SystemContext.Provider>
  )
}

export const useSystemContext = () => {
  const context = useContext(SystemContext)
  if (!context) {
    throw new Error('useSystemContext must be used within a SystemContextProvider')
  }
  return context
}