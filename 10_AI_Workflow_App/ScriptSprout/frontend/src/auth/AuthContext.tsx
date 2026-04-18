/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import {
  ApiError,
  getMe,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from '../services/authApi'
import type { AuthCredentials, AuthUser, RegisterResponse } from '../types/auth'

type AuthContextValue = {
  user: AuthUser | null
  isLoading: boolean
  error: string | null
  clearError: () => void
  login: (credentials: AuthCredentials) => Promise<void>
  register: (credentials: AuthCredentials) => Promise<RegisterResponse>
  logout: () => Promise<void>
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function authErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'Invalid username or password.'
    }
    if (error.status === 409) {
      return 'Username already registered.'
    }
    if (error.status === 403) {
      return error.message
    }
    return error.message
  }
  return 'Could not complete auth request.'
}

/**
 * Execute the function's primary application behavior.
 *
 * @param { children } Input value used to perform this operation.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const refreshMe = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const me = await getMe()
      setUser(me)
    } catch {
      setError('Could not load session state.')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshMe()
  }, [refreshMe])

  const login = useCallback(async (credentials: AuthCredentials) => {
    setError(null)
    try {
      const nextUser = await loginRequest(credentials)
      setUser(nextUser)
    } catch (error_: unknown) {
      setError(authErrorMessage(error_))
      throw error_
    }
  }, [])

  const register = useCallback(async (credentials: AuthCredentials) => {
    setError(null)
    try {
      const result = await registerRequest(credentials)
      setUser(null)
      return result
    } catch (error_: unknown) {
      setError(authErrorMessage(error_))
      throw error_
    }
  }, [])

  const logout = useCallback(async () => {
    setError(null)
    try {
      await logoutRequest()
      setUser(null)
    } catch (error_: unknown) {
      setError(authErrorMessage(error_))
      throw error_
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      error,
      clearError,
      login,
      register,
      logout,
      refreshMe,
    }),
    [user, isLoading, error, clearError, login, register, logout, refreshMe],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Execute the function's primary application behavior.
 * @returns Result generated for the caller.
 */
export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (value === null) {
    throw new Error('useAuth must be used within <AuthProvider>')
  }
  return value
}
