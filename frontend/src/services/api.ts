const envApiBase = import.meta.env.VITE_API_BASE_URL?.trim()

// Determine the API base URL
let normalizedApiBase: string
if (envApiBase) {
  normalizedApiBase = envApiBase.replace(/\/+$/, '')
} else if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  // Development environment
  normalizedApiBase = '/api/v1'
} else if (typeof window !== 'undefined' && window.location.hostname.includes('vercel')) {
  // Production environment on Vercel - use the production backend URL
  normalizedApiBase = 'https://aipad-api.onrender.com/api/v1'
} else {
  // Fallback
  normalizedApiBase = '/api/v1'
}

export const API_BASE = normalizedApiBase
const TOKEN_KEY = 'ai-portfolio-token'
const USER_KEY = 'ai-portfolio-user'

export const getAuthHeaders = (): Record<string, string> => {
  const token = window.localStorage.getItem(TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const clearSession = (): void => {
  window.localStorage.removeItem(TOKEN_KEY)
  window.localStorage.removeItem(USER_KEY)
}

const redirectToSignIn = (): void => {
  if (window.location.pathname !== '/signin') {
    window.location.assign('/signin')
  }
}

const handleUnauthorized = (): void => {
  clearSession()
  redirectToSignIn()
}

type ApiErrorPayload = {
  detail?: string
  message?: string
  error?: string | { message?: string }
}

export const requestJson = async <T>(
  path: string,
  options: RequestInit = {},
): Promise<T> => {
  const headers: Record<string, string> = {
    ...getAuthHeaders(),
    ...(options.headers as Record<string, string> | undefined),
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    handleUnauthorized()
    throw new Error('Session expired or invalid token. Please sign in again.')
  }

  const payload = (await response.json().catch(() => null)) as (T & ApiErrorPayload) | null

  if (!response.ok) {
    throw new Error(
      payload?.detail ||
        (typeof payload?.error === 'string' ? payload.error : payload?.error?.message) ||
        payload?.message ||
        `Request failed for ${path} (${response.status})`,
    )
  }

  if (payload === null) {
    throw new Error(`Request failed for ${path}: empty response payload`)
  }

  return payload as T
}

export const fetchAuthJson = async <T>(path: string): Promise<T> => {
  return requestJson<T>(path)
}
