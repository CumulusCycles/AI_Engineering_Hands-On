import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

/**
 * Execute the function's primary application behavior.
 *
 * @param { children } Input value used to perform this operation.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout, isLoading } = useAuth();
  const location = useLocation();
  const isAuthor = user?.role === "author";
  const isAdmin = user?.role === "admin";
  const year = new Date().getFullYear();
  const isAuthPage =
    location.pathname === "/login" || location.pathname === "/register";

  return (
    <div className="app-frame">
      <header className="topbar">
        <div className="brand-lockup">
          <img
            className="brand-mark"
            src="/images/icon_transparent.png"
            alt="ScriptSprout"
          />
          <div className="brand-copy">
            <strong>ScriptSprout</strong>
            <span>AI authoring workspace</span>
          </div>
        </div>

        <nav className="nav" aria-label="Primary">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Home
          </NavLink>
          {isAuthor && (
            <NavLink
              to="/studio"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Author studio
            </NavLink>
          )}
          {isAuthor && (
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Profile
            </NavLink>
          )}
          {isAdmin && (
            <NavLink
              to="/admin-dashboard"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Admin dashboard
            </NavLink>
          )}
          {isAdmin && (
            <NavLink
              to="/admin-nlp"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Admin NLP query
            </NavLink>
          )}
          {!user && (
            <NavLink
              to="/login"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Login
            </NavLink>
          )}
          {!user && (
            <NavLink
              to="/register"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Register
            </NavLink>
          )}
          {user && (
            <span className="user-pill">
              {user.username} ({user.role})
            </span>
          )}
          {user && (
            <button
              type="button"
              className="linklike"
              onClick={() => {
                void logout();
              }}
              disabled={isLoading}
            >
              Logout
            </button>
          )}
        </nav>
      </header>

      <section className="hero">
        <img className="hero-logo" src="/images/logo.png" alt="ScriptSprout" />
        <p>From Prompt to YouTube-Ready Story Content</p>
        <span className="hero-divider" aria-hidden="true" />
        <p className="hero-subtle">
          Plant a prompt. Grow a channel-ready story.
        </p>
      </section>

      <main
        className={`content-shell${isAuthPage ? " content-shell-narrow" : ""}`}
      >
        <section className="panel">{children}</section>
      </main>

      <footer className="footer">
        <div className="footer-brand">
          <img
            className="footer-logo"
            src="/images/icon_transparent.png"
            alt=""
            aria-hidden="true"
          />
          <span>ScriptSprout © {year}</span>
        </div>
      </footer>
    </div>
  );
}
