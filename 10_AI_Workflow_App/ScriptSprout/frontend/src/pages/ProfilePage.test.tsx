import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ProfilePage } from "./ProfilePage";

/* ------------------------------------------------------------------ */
/*  mocks                                                             */
/* ------------------------------------------------------------------ */

let mockUser: {
  username: string;
  role: string;
  email?: string | null;
  email_verified?: boolean;
} | null = null;
const mockLogout = vi.fn(() => Promise.resolve());
const mockNavigate = vi.fn();

vi.mock("../auth/AuthContext", () => ({
  useAuth: () => ({
    user: mockUser,
    logout: mockLogout,
  }),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockChangePassword = vi.fn();
const mockChangeEmail = vi.fn();

vi.mock("../services/authApi", () => ({
  ApiError: class extends Error {
    readonly status: number;
    constructor(message: string, status: number) {
      super(message);
      this.status = status;
    }
  },
  changePassword: (...args: unknown[]) => mockChangePassword(...args),
  changeEmail: (...args: unknown[]) => mockChangeEmail(...args),
}));

afterEach(() => {
  mockUser = null;
  cleanup();
  vi.restoreAllMocks();
  mockChangePassword.mockReset();
  mockChangeEmail.mockReset();
  mockLogout.mockReset().mockReturnValue(Promise.resolve());
  mockNavigate.mockReset();
});

/* ------------------------------------------------------------------ */
/*  helpers                                                           */
/* ------------------------------------------------------------------ */

function renderPage() {
  return render(
    <MemoryRouter>
      <ProfilePage />
    </MemoryRouter>,
  );
}

/* ------------------------------------------------------------------ */
/*  tests                                                             */
/* ------------------------------------------------------------------ */

describe("ProfilePage", () => {
  it("displays username and email with verified badge", () => {
    mockUser = {
      username: "alice",
      role: "author",
      email: "a@b.com",
      email_verified: true,
    };
    renderPage();
    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("a@b.com")).toBeInTheDocument();
    expect(screen.getByText("(verified)")).toBeInTheDocument();
  });

  it("shows unverified badge when email is not verified", () => {
    mockUser = {
      username: "bob",
      role: "author",
      email: "b@c.com",
      email_verified: false,
    };
    renderPage();
    expect(screen.getByText("(unverified)")).toBeInTheDocument();
  });

  it("shows (not set) when email is null", () => {
    mockUser = { username: "carol", role: "author", email: null };
    renderPage();
    expect(screen.getByText("(not set)")).toBeInTheDocument();
  });

  it("change password form submits and navigates to /login", async () => {
    mockUser = {
      username: "dave",
      role: "author",
      email: "d@e.com",
      email_verified: true,
    };
    mockChangePassword.mockResolvedValue({
      message: "Password changed. Please log in again.",
    });

    renderPage();

    fireEvent.change(screen.getByLabelText("Current password"), {
      target: { value: "OldPass1" },
    });
    fireEvent.change(screen.getByLabelText("New password"), {
      target: { value: "NewPass2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Change password" }));

    await waitFor(() => {
      expect(mockChangePassword).toHaveBeenCalledWith("OldPass1", "NewPass2");
    });
    expect(
      screen.getByText("Password changed. Please log in again."),
    ).toBeInTheDocument();

    // After the timeout the user should be logged out and redirected
    await waitFor(
      () => {
        expect(mockLogout).toHaveBeenCalled();
      },
      { timeout: 3000 },
    );
  });

  it("shows error when change password returns 401", async () => {
    mockUser = {
      username: "eve",
      role: "author",
      email: "e@f.com",
      email_verified: true,
    };
    const { ApiError } = await import("../services/authApi");
    mockChangePassword.mockRejectedValue(new ApiError("bad", 401));

    renderPage();

    fireEvent.change(screen.getByLabelText("Current password"), {
      target: { value: "Wrong1" },
    });
    fireEvent.change(screen.getByLabelText("New password"), {
      target: { value: "NewPass2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Change password" }));

    await waitFor(() => {
      expect(
        screen.getByText("Current password is incorrect."),
      ).toBeInTheDocument();
    });
  });

  it("change email submits and navigates to verify-email", async () => {
    mockUser = {
      username: "fay",
      role: "author",
      email: "f@g.com",
      email_verified: true,
    };
    mockChangeEmail.mockResolvedValue({
      message: "ok",
      delivery_channel: "email",
      preview_token: "tok-abc",
    });

    renderPage();

    fireEvent.change(screen.getByLabelText("New email"), {
      target: { value: "new@x.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Change email" }));

    await waitFor(() => {
      expect(mockChangeEmail).toHaveBeenCalledWith("new@x.com");
      expect(mockNavigate).toHaveBeenCalledWith(
        "/verify-email?username=fay&token=tok-abc",
      );
    });
  });

  it("shows error when change email returns 409", async () => {
    mockUser = {
      username: "gus",
      role: "author",
      email: "g@h.com",
      email_verified: true,
    };
    const { ApiError } = await import("../services/authApi");
    mockChangeEmail.mockRejectedValue(new ApiError("conflict", 409));

    renderPage();

    fireEvent.change(screen.getByLabelText("New email"), {
      target: { value: "dup@x.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Change email" }));

    await waitFor(() => {
      expect(
        screen.getByText("That email is already in use."),
      ).toBeInTheDocument();
    });
  });

  it("buttons are disabled when fields are empty", () => {
    mockUser = {
      username: "hal",
      role: "author",
      email: "h@i.com",
      email_verified: true,
    };
    renderPage();
    expect(
      screen.getByRole("button", { name: "Change password" }),
    ).toBeDisabled();
    expect(screen.getByRole("button", { name: "Change email" })).toBeDisabled();
  });
});
