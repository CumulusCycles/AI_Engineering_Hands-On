import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  ApiError,
  confirmEmailVerification,
  requestEmailVerification,
} from "../services/authApi";

/**
 * Render author email verification workflow page.
 *
 * @returns Email verification page component.
 */
export function EmailVerificationPage() {
  const [searchParams] = useSearchParams();
  const presetUsername = searchParams.get("username") ?? "";
  const presetToken = searchParams.get("token") ?? "";
  const [username, setUsername] = useState(presetUsername);
  const [email, setEmail] = useState("");
  const [token, setToken] = useState(presetToken);
  const [message, setMessage] = useState<string | null>(null);
  const [previewToken, setPreviewToken] = useState<string | null>(
    presetToken || null,
  );
  const [copied, setCopied] = useState(false);
  const [verificationSuccess, setVerificationSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [requesting, setRequesting] = useState(false);
  const [verifying, setVerifying] = useState(false);

  /**
   * Request a verification token to be delivered by email.
   *
   * @param event Form submit event.
   */
  async function onRequestToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setPreviewToken(null);
    setCopied(false);
    setVerificationSuccess(false);
    setRequesting(true);
    try {
      const response = await requestEmailVerification(username, email);
      setMessage(response.message);
      if (response.preview_token) {
        setPreviewToken(response.preview_token);
      }
    } catch (error_: unknown) {
      if (error_ instanceof ApiError) {
        setError(error_.message);
      } else {
        setError("Could not request verification email.");
      }
    } finally {
      setRequesting(false);
    }
  }

  /**
   * Confirm email ownership with one-time verification token.
   *
   * @param event Form submit event.
   */
  async function onVerifyToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setVerificationSuccess(false);
    setVerifying(true);
    try {
      const response = await confirmEmailVerification(username, token);
      setMessage(response.message);
      setVerificationSuccess(true);
      setToken("");
    } catch (error_: unknown) {
      if (error_ instanceof ApiError) {
        setError(error_.message);
      } else {
        setError("Could not verify email token.");
      }
    } finally {
      setVerifying(false);
    }
  }

  return (
    <>
      <h2>Verify your email</h2>
      <p className="muted">
        Enter your email to receive a verification token, then confirm the token
        to activate login.
      </p>

      <form
        className="auth-form"
        onSubmit={(event) => void onRequestToken(event)}
      >
        <label>
          Username
          <input
            name="username"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            name="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={requesting}>
          {requesting ? "Sending..." : "Send verification token"}
        </button>
      </form>

      {previewToken && (
        <section className="group" data-testid="preview-token">
          <h3>Your verification token</h3>
          <p className="muted">
            No email server is configured. Copy the token below and paste it
            into the verification field.
          </p>
          <div className="token-row">
            <code className="token-value">{previewToken}</code>
            <button
              type="button"
              className="copy-btn"
              title="Copy token"
              onClick={() => {
                void navigator.clipboard.writeText(previewToken).then(() => {
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2000);
                });
              }}
            >
              {copied ? "✓ Copied" : "📋 Copy"}
            </button>
          </div>
        </section>
      )}

      <form
        className="auth-form"
        onSubmit={(event) => void onVerifyToken(event)}
      >
        <label>
          Verification token
          <input
            name="token"
            autoComplete="one-time-code"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={verifying}>
          {verifying ? "Verifying..." : "Verify email"}
        </button>
      </form>

      {message && <p className="ok">{message}</p>}
      {verificationSuccess && (
        <p className="ok" data-testid="verification-success">
          Verified successfully. <Link to="/login">Continue to login</Link>.
        </p>
      )}
      {error && <p className="err">{error}</p>}

      <p className="muted">
        Verified already? <Link to="/login">Login</Link>.
      </p>
    </>
  );
}
