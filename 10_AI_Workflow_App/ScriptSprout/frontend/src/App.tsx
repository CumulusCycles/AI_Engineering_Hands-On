import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { useAuth } from "./auth/AuthContext";
import { AppShell } from "./layout/AppShell";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AdminNlpQueryPage } from "./pages/AdminNlpQueryPage";
import { AuthorStudioPage } from "./pages/AuthorStudioPage";
import { EmailVerificationPage } from "./pages/EmailVerificationPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";

/**
 * Execute the function's primary application behavior.
 */
function App() {
  const { user } = useAuth();
  const isAuthor = user?.role === "author";
  const isAdmin = user?.role === "admin";

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/login"
          element={user ? <Navigate to="/" replace /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={user ? <Navigate to="/" replace /> : <RegisterPage />}
        />
        <Route path="/verify-email" element={<EmailVerificationPage />} />
        <Route
          path="/studio"
          element={
            !user ? (
              <Navigate to="/login" replace />
            ) : isAuthor ? (
              <AuthorStudioPage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route
          path="/profile"
          element={
            !user ? (
              <Navigate to="/login" replace />
            ) : isAuthor ? (
              <ProfilePage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route path="/workspace" element={<Navigate to="/studio" replace />} />
        <Route
          path="/draft-review"
          element={<Navigate to="/studio" replace />}
        />
        <Route
          path="/story-media"
          element={<Navigate to="/studio" replace />}
        />
        <Route
          path="/admin-dashboard"
          element={
            !user ? (
              <Navigate to="/login" replace />
            ) : isAdmin ? (
              <AdminDashboardPage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route
          path="/admin-nlp"
          element={
            !user ? (
              <Navigate to="/login" replace />
            ) : isAdmin ? (
              <AdminNlpQueryPage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}

export default App;
