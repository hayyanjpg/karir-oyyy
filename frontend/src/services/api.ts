import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function getAccessToken(): string | null {
  return accessToken
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  try {
    const { data } = await axios.post<{ access_token: string }>(
      `${API_BASE_URL}/auth/refresh`,
      null,
      { withCredentials: true },
    )
    setAccessToken(data.access_token)
    return data.access_token
  } catch {
    setAccessToken(null)
    return null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined
    const status = error.response?.status
    const url = original?.url ?? ''

    if (status === 401 && original && !original._retry && !url.includes('/auth/')) {
      original._retry = true
      refreshPromise =
        refreshPromise ??
        refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      const token = await refreshPromise
      if (!token) {
        return Promise.reject(error)
      }
      original.headers.Authorization = `Bearer ${token}`
      return api(original)
    }

    return Promise.reject(error)
  },
)

interface ApiErrorBody {
  detail?: string | Array<{ msg?: string }>
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiErrorBody>(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg ?? 'Input tidak valid').join(', ')
    }
    if (error.response?.status === 413) {
      return 'Data terlalu besar untuk diekspor. Persempit filter terlebih dahulu.'
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Tidak dapat terhubung ke server. Periksa koneksi atau konfigurasi API.'
    }
    return error.message || 'Permintaan gagal.'
  }
  return error instanceof Error ? error.message : 'Terjadi kesalahan yang tidak diketahui.'
}

export default api
