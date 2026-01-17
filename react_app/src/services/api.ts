import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface ReadingSessionStartResponse {
  session_id: number
  status: string
}

export interface ReadingSessionHeartbeatResponse {
  status: string
}

export interface ReadingSessionEndResponse {
  status: string
}

export const readingStatsApi = {
  startSession: async (bookId: number): Promise<ReadingSessionStartResponse> => {
    const response = await api.post('/api/stats/session/start', { book_id: bookId })
    return response.data
  },

  sendHeartbeat: async (
    sessionId: number,
    durationSeconds: number,
    progress: number,
    position?: string
  ): Promise<ReadingSessionHeartbeatResponse> => {
    const response = await api.post('/api/stats/session/heartbeat', {
      session_id: sessionId,
      duration_seconds: durationSeconds,
      progress,
      position,
    })
    return response.data
  },

  endSession: async (
    sessionId: number,
    durationSeconds: number,
    progress: number,
    position?: string
  ): Promise<ReadingSessionEndResponse> => {
    const response = await api.post('/api/stats/session/end', {
      session_id: sessionId,
      duration_seconds: durationSeconds,
      progress,
      position,
    })
    return response.data
  },
}

export default api
