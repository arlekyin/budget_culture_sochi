import React, { createContext, useContext, useEffect, useState } from 'react'
import api from '@/lib/api'

export interface UserInstitution {
  id: number
  name: string
}

export interface AuthUser {
  id: number
  username: string
  firstName: string
  lastName: string
  role: string
  roleDisplay: string
  institution: UserInstitution | null
}

interface AuthContextValue {
  user: AuthUser | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Восстанавливаем сессию при загрузке
  useEffect(() => {
    api
      .get<AuthUser>('/api/auth/me/')
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = async (username: string, password: string): Promise<void> => {
    // Сначала запрашиваем CSRF-cookie
    try {
      await api.get('/api/auth/me/')
    } catch {
      // Игнорируем 401 — нам нужен только cookie
    }
    const res = await api.post<AuthUser>('/api/auth/login/', { username, password })
    setUser(res.data)
  }

  const logout = async (): Promise<void> => {
    await api.post('/api/auth/logout/')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
