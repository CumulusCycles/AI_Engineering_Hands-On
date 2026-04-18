import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

/**
 * Execute the function's primary application behavior.
 */
export function LoginPage() {
  const navigate = useNavigate()
  const { login, error, clearError } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    clearError()
  }, [clearError])

  /**
   * Execute the function's primary application behavior.
   *
   * @param event Input value used to perform this operation.
   */
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    clearError()
    setSubmitting(true)
    try {
      await login({ username, password })
      navigate('/')
    } catch (error: unknown) {
      // Recover unverified users by routing directly to email verification.
      if (
        typeof error === 'object'
        && error !== null
        && 'status' in error
        && (error as { status?: number }).status === 403
      ) {
        navigate(`/verify-email?username=${encodeURIComponent(username.trim())}`)
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <h2>Login</h2>
      <form className="auth-form" onSubmit={(event) => void onSubmit(event)}>
        <label>
          Username
          <input
            autoFocus
            name="username"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        {error && <p className="err">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="muted">
        Need an account? <Link to="/register">Register</Link>.
      </p>
    </>
  )
}
