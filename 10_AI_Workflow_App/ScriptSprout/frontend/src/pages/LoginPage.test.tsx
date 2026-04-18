import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LoginPage } from './LoginPage'

const mockNavigate = vi.fn()
const mockLogin = vi.fn()
const mockClearError = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    error: null,
    clearError: mockClearError,
  }),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('LoginPage', () => {
  it('redirects to verify-email when login is blocked by verification gate', async () => {
    mockLogin.mockRejectedValueOnce({ status: 403 })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'author_1' },
    })
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))

    await screen.findByRole('button', { name: 'Sign in' })
    expect(mockNavigate).toHaveBeenCalledWith('/verify-email?username=author_1')
  })
})

