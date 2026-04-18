import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { EmailVerificationPage } from "./EmailVerificationPage";

const requestEmailVerificationMock = vi.fn();
const confirmEmailVerificationMock = vi.fn();

vi.mock("../services/authApi", () => ({
  ApiError: class ApiError extends Error {
    constructor(
      message: string,
      public status: number,
    ) {
      super(message);
    }
  },
  requestEmailVerification: (...args: unknown[]) =>
    requestEmailVerificationMock(...args),
  confirmEmailVerification: (...args: unknown[]) =>
    confirmEmailVerificationMock(...args),
}));

describe("EmailVerificationPage", () => {
  it("requests token then confirms verification", async () => {
    requestEmailVerificationMock.mockResolvedValueOnce({
      message: "Verification token generated.",
      delivery_channel: "email",
      preview_token: "test-preview-token-abc",
    });
    confirmEmailVerificationMock.mockResolvedValueOnce({
      message: "Email verified successfully.",
    });

    render(
      <MemoryRouter initialEntries={["/verify-email?username=author_1"]}>
        <EmailVerificationPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "author_1@example.com" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Send verification token" }),
    );

    await waitFor(() => {
      expect(requestEmailVerificationMock).toHaveBeenCalledWith(
        "author_1",
        "author_1@example.com",
      );
    });
    expect(screen.getByTestId("preview-token")).toBeInTheDocument();
    expect(screen.getByText("test-preview-token-abc")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Verification token"), {
      target: { value: "my-token-from-email" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Verify email" }));

    await waitFor(() => {
      expect(confirmEmailVerificationMock).toHaveBeenCalledWith(
        "author_1",
        "my-token-from-email",
      );
    });
    expect(
      screen.getByText("Email verified successfully."),
    ).toBeInTheDocument();
    expect(screen.getByTestId("verification-success")).toBeInTheDocument();
  });
});
