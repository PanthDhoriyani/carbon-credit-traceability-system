import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  r => r.data,
  err => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)))
  }
)

export const submitEmission = (data) => api.post('/submissions/', data)
export const getSubmissions = (params = {}) => api.get('/submissions/', { params })
export const getSubmission = (id) => api.get(`/submissions/${id}`)
export const getDashboardStats = () => api.get('/dashboard/stats')
export const getRecentSubmissions = (limit = 8) => api.get(`/dashboard/recent?limit=${limit}`)
export const getCreditsByMaterial = () => api.get('/dashboard/credits-by-material')
export const getBaselineFactors = () => api.get('/baseline-factors')
export const getHealth = () => api.get('/health')

export default api
