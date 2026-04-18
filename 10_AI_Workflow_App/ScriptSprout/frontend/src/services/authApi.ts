import type {
  AuthCredentials,
  ChangeEmailResponse,
  ChangePasswordResponse,
  EmailVerificationConfirmResponse,
  AuthUser,
  EmailVerificationRequestResponse,
  RegisterResponse,
} from "../types/auth";

/**
 * Carry backend HTTP status and detail text for UI-friendly error handling.
 */
export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

/**
 * Execute the function's primary application behavior.
 *
 * @param response Outgoing HTTP response to mutate headers/cookies.
 * @returns Result generated for the caller.
 */
async function readJson(
  response: Response,
): Promise<Record<string, unknown> | undefined> {
  const text = await response.text();
  if (!text) {
    return undefined;
  }
  return JSON.parse(text) as Record<string, unknown>;
}

/**
 * Execute the function's primary application behavior.
 *
 * @param input Request input payload for downstream API calls.
 * @param init? Input value used to perform this operation.
 * @returns Result generated for the caller.
 */
async function request(input: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(input, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (response.ok) {
    return response;
  }

  const payload = await readJson(response);
  const detail =
    typeof payload?.detail === "string" ? payload.detail : response.statusText;
  throw new ApiError(detail || "Request failed", response.status);
}

/**
 * Execute the function's primary application behavior.
 *
 * @param credentials Username/password credentials submitted by the user.
 * @returns Result generated for the caller.
 */
export async function register(
  credentials: AuthCredentials,
): Promise<RegisterResponse> {
  const response = await request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  return (await response.json()) as RegisterResponse;
}

/**
 * Request email verification token delivery for an author account.
 *
 * @param username Author username that just registered.
 * @param email Email destination for verification.
 * @returns Delivery metadata confirming the token was queued.
 */
export async function requestEmailVerification(
  username: string,
  email: string,
): Promise<EmailVerificationRequestResponse> {
  const response = await request("/api/auth/email-verification/request", {
    method: "POST",
    body: JSON.stringify({ username, email }),
  });
  return (await response.json()) as EmailVerificationRequestResponse;
}

/**
 * Confirm email verification with one-time token.
 *
 * @param username Author username being verified.
 * @param token Verification token submitted by the user.
 */
export async function confirmEmailVerification(
  username: string,
  token: string,
): Promise<EmailVerificationConfirmResponse> {
  const response = await request("/api/auth/email-verification/confirm", {
    method: "POST",
    body: JSON.stringify({ username, token }),
  });
  return (await response.json()) as EmailVerificationConfirmResponse;
}

/**
 * Execute the function's primary application behavior.
 *
 * @param credentials Username/password credentials submitted by the user.
 * @returns Result generated for the caller.
 */
export async function login(credentials: AuthCredentials): Promise<AuthUser> {
  const response = await request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  return (await response.json()) as AuthUser;
}

/**
 * Execute the function's primary application behavior.
 * @returns Result generated for the caller.
 */
export async function logout(): Promise<void> {
  await request("/api/auth/logout", { method: "POST" });
}

/**
 * Retrieve data needed for this operation.
 * @returns Result generated for the caller.
 */
export async function getMe(): Promise<AuthUser | null> {
  try {
    const response = await request("/api/auth/me");
    return (await response.json()) as AuthUser;
  } catch (error: unknown) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

/**
 * Change the authenticated user's password. Invalidates all sessions.
 *
 * @param currentPassword The user's current password.
 * @param newPassword The desired new password.
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<ChangePasswordResponse> {
  const response = await request("/api/auth/password", {
    method: "PUT",
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
  return (await response.json()) as ChangePasswordResponse;
}

/**
 * Change the authenticated user's email. Requires re-verification.
 *
 * @param newEmail The new email address.
 */
export async function changeEmail(
  newEmail: string,
): Promise<ChangeEmailResponse> {
  const response = await request("/api/auth/email", {
    method: "PUT",
    body: JSON.stringify({ new_email: newEmail }),
  });
  return (await response.json()) as ChangeEmailResponse;
}
