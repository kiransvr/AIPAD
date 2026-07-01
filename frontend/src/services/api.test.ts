import { beforeEach, describe, expect, it, vi } from 'vitest'

import { clearSession, getAuthHeaders, requestJson } from './api'

const makeStorage = () => {
  const store = new Map<string, string>()
  return {
    getItem: (key: string) => (store.has(key) ? store.get(key)! : null),
    setItem: (key: string, value: string) => {
      store.set(key, value)
    },
    removeItem: (key: string) => {
      store.delete(key)
    },
    clear: () => {
      store.clear()
    },
  }
}

describe('api service auth handling', () => {
  const assign = vi.fn()
  const localStorage = makeStorage()

  beforeEach(() => {
    assign.mockReset()
    localStorage.clear()

    vi.stubGlobal('window', {
      localStorage,
      location: {
        pathname: '/',
        assign,
      },
    })
  })

  it('getAuthHeaders returns bearer header when token exists', () => {
    localStorage.setItem('ai-portfolio-token', 'token-123')
    expect(getAuthHeaders()).toEqual({ Authorization: 'Bearer token-123' })
  })

  it('clearSession removes persisted auth keys', () => {
    localStorage.setItem('ai-portfolio-token', 'token-123')
    localStorage.setItem('ai-portfolio-user', '{"username":"admin"}')

    clearSession()

    expect(localStorage.getItem('ai-portfolio-token')).toBeNull()
    expect(localStorage.getItem('ai-portfolio-user')).toBeNull()
  })

  it('requestJson redirects to signin on 401 responses', async () => {
    localStorage.setItem('ai-portfolio-token', 'expired-token')

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        status: 401,
        ok: false,
        json: async () => ({ error: { message: 'Not authenticated' } }),
      }),
    )

    await expect(requestJson('/par/summary')).rejects.toThrow('Session expired or invalid token')
    expect(assign).toHaveBeenCalledWith('/signin')
    expect(localStorage.getItem('ai-portfolio-token')).toBeNull()
  })

  it('requestJson extracts standardized backend error messages', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        status: 400,
        ok: false,
        json: async () => ({ error: { message: 'Bad request payload' } }),
      }),
    )

    await expect(requestJson('/upload')).rejects.toThrow('Bad request payload')
  })
})
