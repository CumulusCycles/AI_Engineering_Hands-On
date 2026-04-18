import { render, screen } from '@testing-library/react'
import { cleanup } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'

vi.mock('./auth/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('./layout/AppShell', () => ({
  AppShell: ({ children }: { children: ReactNode }) => <>{children}</>,
}))

vi.mock('./pages/HomePage', () => ({
  HomePage: () => <h2>Home page</h2>,
}))
vi.mock('./pages/LoginPage', () => ({
  LoginPage: () => <h2>Login page</h2>,
}))
vi.mock('./pages/RegisterPage', () => ({
  RegisterPage: () => <h2>Register page</h2>,
}))
vi.mock('./pages/EmailVerificationPage', () => ({
  EmailVerificationPage: () => <h2>Email verification page</h2>,
}))
vi.mock('./pages/AuthorStudioPage', () => ({
  AuthorStudioPage: () => <h2>Author studio page</h2>,
}))
vi.mock('./pages/AdminDashboardPage', () => ({
  AdminDashboardPage: () => <h2>Admin dashboard page</h2>,
}))
vi.mock('./pages/AdminNlpQueryPage', () => ({
  AdminNlpQueryPage: () => <h2>Admin NLP page</h2>,
}))

import { useAuth } from './auth/AuthContext'
import App from './App'

const useAuthMock = vi.mocked(useAuth)

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('App route guards', () => {
  it('redirects anonymous users from all protected routes to login', () => {
    useAuthMock.mockReturnValue({
      user: null,
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      login: vi.fn(async () => {}),
      register: vi.fn(async () => {}),
      logout: vi.fn(async () => {}),
      refreshMe: vi.fn(async () => {}),
    })

    const protectedRoutes = [
      '/studio',
      '/workspace',
      '/draft-review',
      '/story-media',
      '/admin-dashboard',
      '/admin-nlp',
    ]
    for (const route of protectedRoutes) {
      render(
        <MemoryRouter initialEntries={[route]}>
          <App />
        </MemoryRouter>,
      )
      expect(screen.getByRole('heading', { name: 'Login page' })).toBeInTheDocument()
      cleanup()
    }
  })

  it('redirects author away from admin route', () => {
    useAuthMock.mockReturnValue({
      user: {
        id: 1,
        username: 'author_1',
        email: 'author_1@example.com',
        email_verified: true,
        role: 'author',
        is_active: true,
      },
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      login: vi.fn(async () => {}),
      register: vi.fn(async () => {}),
      logout: vi.fn(async () => {}),
      refreshMe: vi.fn(async () => {}),
    })

    render(
      <MemoryRouter initialEntries={['/admin-dashboard']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Home page' })).toBeInTheDocument()
  })

  it('redirects admin away from author route', () => {
    useAuthMock.mockReturnValue({
      user: {
        id: 2,
        username: 'admin_1',
        email: null,
        email_verified: true,
        role: 'admin',
        is_active: true,
      },
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      login: vi.fn(async () => {}),
      register: vi.fn(async () => {}),
      logout: vi.fn(async () => {}),
      refreshMe: vi.fn(async () => {}),
    })

    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Home page' })).toBeInTheDocument()
  })

  it('allows admin routes for admin users', () => {
    useAuthMock.mockReturnValue({
      user: {
        id: 2,
        username: 'admin_1',
        email: null,
        email_verified: true,
        role: 'admin',
        is_active: true,
      },
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      login: vi.fn(async () => {}),
      register: vi.fn(async () => {}),
      logout: vi.fn(async () => {}),
      refreshMe: vi.fn(async () => {}),
    })

    render(
      <MemoryRouter initialEntries={['/admin-dashboard']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Admin dashboard page' })).toBeInTheDocument()
    cleanup()

    render(
      <MemoryRouter initialEntries={['/admin-nlp']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Admin NLP page' })).toBeInTheDocument()
  })

  it('allows author routes for author users', () => {
    useAuthMock.mockReturnValue({
      user: {
        id: 1,
        username: 'author_1',
        email: 'author_1@example.com',
        email_verified: true,
        role: 'author',
        is_active: true,
      },
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      login: vi.fn(async () => {}),
      register: vi.fn(async () => {}),
      logout: vi.fn(async () => {}),
      refreshMe: vi.fn(async () => {}),
    })

    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Author studio page' })).toBeInTheDocument()
    cleanup()

    render(
      <MemoryRouter initialEntries={['/draft-review']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Author studio page' })).toBeInTheDocument()
    cleanup()

    render(
      <MemoryRouter initialEntries={['/story-media']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: 'Author studio page' })).toBeInTheDocument()
  })
})
