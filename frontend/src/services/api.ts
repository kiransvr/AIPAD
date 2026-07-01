export const API_BASE = 'http://localhost:8000/api/v1'

export const getAuthHeaders = (): Record<string, string> => {
  const token = window.localStorage.getItem('ai-portfolio-token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const fetchAuthJson = async <T>(path: string): Promise<T> => {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      ...getAuthHeaders(),
    },
  })

  const payload = (await res.json().catch(() => null)) as T | null

  if (!res.ok || payload === null) {
    throw new Error(`Request failed for ${path} (${res.status})`)
  }

  return payload
}
