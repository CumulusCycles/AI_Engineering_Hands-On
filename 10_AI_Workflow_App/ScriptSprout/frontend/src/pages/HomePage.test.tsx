import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { HomePage } from "./HomePage";

let mockUser: { username: string; role: string } | null = null;
let mockIsLoading = false;

vi.mock("../auth/AuthContext", () => ({
  useAuth: () => ({
    user: mockUser,
    isLoading: mockIsLoading,
  }),
}));

function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}

afterEach(() => {
  mockUser = null;
  mockIsLoading = false;
  cleanup();
  vi.restoreAllMocks();
});

describe("HomePage", () => {
  it("shows anonymous state when not logged in", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ status: "ok", service: "ScriptSprout" }),
    );

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    expect(screen.getByTestId("auth-state-anonymous")).toBeInTheDocument();
  });

  it("shows authenticated state with username and role", async () => {
    mockUser = { username: "alice", role: "author" };
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ status: "ok", service: "ScriptSprout" }),
    );

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    expect(screen.getByTestId("auth-state-authenticated")).toBeInTheDocument();
    expect(screen.getByText(/alice/)).toBeInTheDocument();
  });

  it("shows API health status on success", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ status: "ok", service: "ScriptSprout" }),
    );

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/ScriptSprout/)).toBeInTheDocument();
    });
  });

  it("shows error message when API is unreachable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      new TypeError("Failed to fetch"),
    );

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/API unreachable/)).toBeInTheDocument();
    });
  });

  it("shows error message on non-ok HTTP response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("", { status: 503 }),
    );

    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/HTTP 503/)).toBeInTheDocument();
    });
  });

  it("does not update state after unmount (AbortController)", async () => {
    let resolveHealth!: (value: Response) => void;
    const healthPromise = new Promise<Response>((r) => {
      resolveHealth = r;
    });
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockReturnValue(healthPromise);

    const { unmount } = render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    // Verify fetch was called with an AbortSignal
    expect(fetchSpy).toHaveBeenCalledWith(
      "/health",
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );

    unmount();

    // The abort signal should be triggered on unmount
    const signal = fetchSpy.mock.calls[0][1]?.signal as AbortSignal;
    expect(signal.aborted).toBe(true);

    resolveHealth(jsonResponse({ status: "ok", service: "ScriptSprout" }));
  });
});
