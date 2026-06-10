import axios from 'axios'

// Create base axios instance without auth (for use with token provider)
const baseApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Factory function to create an axios instance with Clerk auth interceptor
// Use this in components with useAuth hook: const api = createApi(getToken)
const createApi = (getToken: () => Promise<string | null>) => {
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

// Export factory for use with Clerk's getToken in React components
export { createApi }

// Default export - base api without auth interceptor
// For authenticated requests, use createApi(getToken) in your component
export default baseApi