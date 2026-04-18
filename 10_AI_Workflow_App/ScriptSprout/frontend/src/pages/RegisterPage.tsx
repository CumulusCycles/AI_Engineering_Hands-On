import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

/**
 * Execute the function's primary application behavior.
 */
export function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    clearError();
  }, [clearError]);

  /**
   * Execute the function's primary application behavior.
   *
   * @param event Input value used to perform this operation.
   */
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError();
    if (password !== confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }
    setLocalError(null);
    setSubmitting(true);
    try {
      const response = await register({ username, password });
      if (response.verification_required) {
        navigate(
          `/verify-email?username=${encodeURIComponent(response.username)}`,
        );
        return;
      }
      navigate("/login");
    } catch (error: unknown) {
      // If the username already exists, route back into verification recovery.
      if (
        typeof error === "object" &&
        error !== null &&
        "status" in error &&
        (error as { status?: number }).status === 409
      ) {
        navigate(
          `/verify-email?username=${encodeURIComponent(username.trim())}`,
        );
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <h2>Register</h2>
      <p className="muted">
        Create an author account to start generating content.
      </p>
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
            autoComplete="new-password"
            minLength={8}
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
              setLocalError(null);
            }}
            required
          />
        </label>
        <span className="hint">
          Min 8 chars; must include uppercase, lowercase, and a digit.
        </span>
        <label>
          Confirm password
          <input
            name="confirm-password"
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={confirmPassword}
            onChange={(event) => {
              setConfirmPassword(event.target.value);
              setLocalError(null);
            }}
            required
          />
        </label>
        {localError && <p className="err">{localError}</p>}
        {error && <p className="err">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Login</Link>.
      </p>
    </>
  );
}
