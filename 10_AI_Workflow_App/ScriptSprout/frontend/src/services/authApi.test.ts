import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, getMe, login, register } from './authApi'

/**
 * Build a JSON response object for fetch mocks.
 *
 * Args:
 *   body: Serializable payload.
 *   init: Optional response init overrides.
 *
 * Returns:
 *   Response containing the encoded JSON payload.
 */
function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('authApi', () => {
  it('returns null for getMe when backend responds 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({ detail: 'Not authenticated' }, { status: 401 }),
    )

    await expect(getMe()).resolves.toBeNull()
  })

  it('throws ApiError for login failures with backend detail', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({ detail: 'Invalid username or password' }, { status: 401 }),
    )

    await expect(
      login({ username: 'author', password: 'bad-password' }),
    ).rejects.toMatchObject({
      status: 401,
      message: 'Invalid username or password',
    } as Partial<ApiError>)
  })

  it('sends register payload and includes cookies', async () => {
    const mockFetch = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({
        username: 'author_1',
        role: 'author',
        verification_required: true,
      }),
    )

    const user = await register({ username: 'author_1', password: 'password123' })

    expect(user.username).toBe('author_1')
    expect(user.verification_required).toBe(true)
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/auth/register',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    )
  })
})
