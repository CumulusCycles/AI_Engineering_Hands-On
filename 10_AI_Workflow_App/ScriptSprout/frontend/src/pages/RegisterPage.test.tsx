import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RegisterPage } from "./RegisterPage";

const mockNavigate = vi.fn();
const mockRegister = vi.fn();
const mockClearError = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom",
    );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../auth/AuthContext", () => ({
  useAuth: () => ({
    register: mockRegister,
    error: null,
    clearError: mockClearError,
  }),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("RegisterPage", () => {
  it("shows password requirements hint", () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    expect(
      screen.getByText(
        "Min 8 chars; must include uppercase, lowercase, and a digit.",
      ),
    ).toBeInTheDocument();
  });

  it("shows a mismatch error and does not submit", async () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Username"), {
      target: { value: "author_1" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm password"), {
      target: { value: "password124" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    expect(
      await screen.findByText("Passwords do not match."),
    ).toBeInTheDocument();
    expect(mockRegister).not.toHaveBeenCalled();
  });

  it("redirects to verify-email when username already exists", async () => {
    mockRegister.mockRejectedValueOnce({ status: 409 });

    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Username"), {
      target: { value: "author_1" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.change(screen.getByLabelText("Confirm password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    await screen.findByRole("button", { name: "Create account" });
    expect(mockNavigate).toHaveBeenCalledWith(
      "/verify-email?username=author_1",
    );
  });
});
