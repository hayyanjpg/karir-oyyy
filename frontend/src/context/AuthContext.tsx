import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import api, { setAccessToken } from '../services/api'
import type { User } from '../types'

interface TokenPayload {
  access_token: string
  user: User
}

interface AuthContextValue {
  user: User | null
  loading: boolean
  loginWithGoogle: (credential: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    api
      .post<TokenPayload>('/auth/refresh')
      .then(({ data }) => {
        if (!active) return
        setAccessToken(data.access_token)
        setUser(data.user)
      })
      .catch(() => {
        if (!active) return
        setAccessToken(null)
        setUser(null)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const loginWithGoogle = useCallback(async (credential: string) => {
    const { data } = await api.post<TokenPayload>('/auth/google', { credential })
    setAccessToken(data.access_token)
    setUser(data.user)
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout')
    } finally {
      setAccessToken(null)
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({ user, loading, loginWithGoogle, logout }),
    [user, loading, loginWithGoogle, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
