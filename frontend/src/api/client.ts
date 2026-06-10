import axios from 'axios'
import { useAuth } from '@clerk/clerk-react'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Create a separate instance for use outside React components
const createApiWithToken = (getToken: () => Promise<string | null>) => {
  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  instance.interceptors.request.use(async (config) => {
    try {
      const token = await getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (error) {
      console.warn('Failed to get Clerk token:', error)
    }
    return config
  })

  return instance
}

// Default export - use this in components with useAuth hook
export default api

// Export factory for use with Clerk's getToken
export { createApiWithToken }

// Axios instance for non-React contexts (will be configured separately)
export const createClerkApi = (getToken: () => Promise<string | null>) => {
  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  instance.interceptors.request.use(async (config) => {
    try {
      const token = await getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (error) {
      console.warn('Failed to get Clerk token:', error)
    }
    return config
  })

  return instance
}