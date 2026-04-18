import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

type Health = { status: string; service: string };

/**
 * Execute the function's primary application behavior.
 *
 * @param error Error object captured from a failed async/API operation.
 * @returns Result generated for the caller.
 */
function healthErrorMessage(error: unknown): string {
  if (error instanceof TypeError) {
    return "API unreachable — start the backend (see repo README).";
  }
  if (error instanceof Error && error.message.startsWith("bad_response:")) {
    const code = error.message.slice("bad_response:".length);
    return `API returned HTTP ${code} — the server responded but /health failed; check backend logs.`;
  }
  return "Could not read API status.";
}

/**
 * Execute the function's primary application behavior.
 */
export function HomePage() {
  const { user, isLoading } = useAuth();
  const isAuthor = user?.role === "author";
  const isAdmin = user?.role === "admin";
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    fetch("/health", { signal: ac.signal })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`bad_response:${response.status}`);
        }
        return response.json() as Promise<Health>;
      })
      .then(setHealth)
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setHealthError(healthErrorMessage(error));
      });
    return () => ac.abort();
  }, []);

  return (
    <>
      <h2>Author shell</h2>
      <p className="muted">
        Auth routing and session state are wired. Author creation flow is
        available in one unified studio page.
      </p>

      <section className="group">
        <h3>Session</h3>
        {isLoading && <p className="muted">Checking session…</p>}
        {!isLoading && user && (
          <>
            <p className="ok" data-testid="auth-state-authenticated">
              Signed in as <strong>{user.username}</strong> ({user.role})
            </p>
            {isAuthor && (
              <p className="muted">
                Continue in <Link to="/studio">Author studio</Link>.
              </p>
            )}
            {isAdmin && (
              <p className="muted">
                Continue in <Link to="/admin-dashboard">Admin dashboard</Link>.
              </p>
            )}
            {isAdmin && (
              <p className="muted">
                Ask analytics questions in{" "}
                <Link to="/admin-nlp">Admin NLP query</Link>.
              </p>
            )}
          </>
        )}
        {!isLoading && !user && (
          <p className="muted" data-testid="auth-state-anonymous">
            Not signed in. Use <Link to="/login">Login</Link> or{" "}
            <Link to="/register">Register</Link>.
          </p>
        )}
      </section>

      <section className="group" aria-live="polite">
        <h3>API status</h3>
        {health && (
          <p className="ok">
            <code>/health</code> → {health.status} ({health.service})
          </p>
        )}
        {healthError && <p className="err">{healthError}</p>}
        {!health && !healthError && <p className="muted">Checking…</p>}
      </section>
    </>
  );
}
