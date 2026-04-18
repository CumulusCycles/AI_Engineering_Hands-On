import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ApiError, changeEmail, changePassword } from "../services/authApi";

function profileErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return "Current password is incorrect.";
    if (error.status === 409) return "That email is already in use.";
    return error.message;
  }
  return "Request failed. Please retry.";
}

export function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const [newEmail, setNewEmail] = useState("");
  const [emailBusy, setEmailBusy] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);

  async function onChangePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordBusy(true);
    setPasswordError(null);
    setPasswordMsg(null);
    try {
      const result = await changePassword(currentPassword, newPassword);
      setPasswordMsg(result.message);
      setCurrentPassword("");
      setNewPassword("");
      // Log out after a brief delay so the user sees the success message
      setTimeout(() => {
        void logout().then(() => navigate("/login"));
      }, 1500);
    } catch (error_: unknown) {
      setPasswordError(profileErrorMessage(error_));
    } finally {
      setPasswordBusy(false);
    }
  }

  async function onChangeEmail(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setEmailBusy(true);
    setEmailError(null);
    try {
      const result = await changeEmail(newEmail);
      setNewEmail("");
      const params = new URLSearchParams({
        username: user?.username ?? "",
      });
      if (result.preview_token) {
        params.set("token", result.preview_token);
      }
      navigate(`/verify-email?${params.toString()}`);
    } catch (error_: unknown) {
      setEmailError(profileErrorMessage(error_));
    } finally {
      setEmailBusy(false);
    }
  }

  return (
    <>
      <h2>Profile</h2>

      <section className="group">
        <h3>Account</h3>
        <p>
          <strong>Username:</strong> {user?.username}
        </p>
        <p>
          <strong>Email:</strong> {user?.email ?? "(not set)"}
          {user?.email && (
            <span className={user.email_verified ? "ok" : "err"}>
              {" "}
              ({user.email_verified ? "verified" : "unverified"})
            </span>
          )}
        </p>
      </section>

      <section className="group">
        <h3>Change password</h3>
        {passwordMsg && <p className="ok">{passwordMsg}</p>}
        {passwordError && <p className="err">{passwordError}</p>}
        <form className="auth-form" onSubmit={(e) => void onChangePassword(e)}>
          <label>
            Current password
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <label>
            New password
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
          </label>
          <button
            type="submit"
            disabled={passwordBusy || !currentPassword || !newPassword}
          >
            {passwordBusy ? "Changing..." : "Change password"}
          </button>
        </form>
      </section>

      <section className="group">
        <h3>Change email</h3>
        {emailError && <p className="err">{emailError}</p>}
        <form className="auth-form" onSubmit={(e) => void onChangeEmail(e)}>
          <label>
            New email
            <input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <button type="submit" disabled={emailBusy || !newEmail}>
            {emailBusy ? "Updating..." : "Change email"}
          </button>
        </form>
      </section>
    </>
  );
}
