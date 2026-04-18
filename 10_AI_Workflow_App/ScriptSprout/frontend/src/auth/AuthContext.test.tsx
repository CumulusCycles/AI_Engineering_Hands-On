import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'

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

/**
 * Render auth context values and actions for integration-style hook tests.
 *
 * Returns:
 *   Lightweight test harness component.
 */
function Harness() {
  const { user, isLoading, error, login } = useAuth()

  return (
    <div>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="username">{user?.username ?? 'none'}</div>
      <div data-testid="error">{error ?? ''}</div>
      <button
        type="button"
        onClick={() => {
          void login({ username: 'author_1', password: 'password123' })
        }}
      >
        Login
      </button>
    </div>
  )
}

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('AuthProvider', () => {
  it('hydrates anonymous state when /me returns 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      jsonResponse({ detail: 'Not authenticated' }, { status: 401 }),
    )

    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>,
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
    })
    expect(screen.getByTestId('username')).toHaveTextContent('none')
  })

  it('updates session after successful login request', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
      const url = String(input)
      if (url.endsWith('/api/auth/me')) {
        return jsonResponse({ detail: 'Not authenticated' }, { status: 401 })
      }
      if (url.endsWith('/api/auth/login') && init?.method === 'POST') {
        return jsonResponse({
          id: 1,
          username: 'author_1',
          email: 'author_1@example.com',
          email_verified: true,
          role: 'author',
          is_active: true,
        })
      }
      return jsonResponse({ detail: 'Unexpected route' }, { status: 404 })
    })

    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>,
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Login' }))

    await waitFor(() => {
      expect(screen.getByTestId('username')).toHaveTextContent('author_1')
    })
  })
})
