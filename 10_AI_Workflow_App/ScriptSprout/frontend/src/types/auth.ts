/**
 * Represent supported app roles.
 */
export type UserRole = "author" | "admin";

/**
 * Represent the authenticated user shape returned by `/api/auth/*`.
 */
export type AuthUser = {
  id: number;
  username: string;
  email: string | null;
  email_verified: boolean;
  role: UserRole;
  is_active: boolean;
};

/**
 * Represent login and register request payloads.
 */
export type AuthCredentials = {
  username: string;
  password: string;
};

export type RegisterResponse = {
  username: string;
  role: UserRole;
  verification_required: boolean;
};

export type EmailVerificationRequestResponse = {
  message: string;
  delivery_channel: string;
  preview_token?: string | null;
};

export type EmailVerificationConfirmResponse = {
  message: string;
};

export type ChangePasswordResponse = {
  message: string;
};

export type ChangeEmailResponse = {
  message: string;
  delivery_channel: string;
  preview_token?: string | null;
};
