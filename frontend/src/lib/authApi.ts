import { apiGet, apiPost, setAccessToken } from "./api";
import type { TokenResponse, UserOut, UserRole } from "./types";

export async function register(input: {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
  role: UserRole;
}): Promise<{ message: string }> {
  return apiPost("/auth/register", input);
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const data = await apiPost<TokenResponse>("/auth/login", { email, password });
  setAccessToken(data.access_token);
  return data;
}

export async function logout(): Promise<void> {
  try {
    await apiPost("/auth/logout");
  } finally {
    setAccessToken(null);
  }
}

export async function logoutAll(): Promise<void> {
  try {
    await apiPost("/auth/logout-all");
  } finally {
    setAccessToken(null);
  }
}

export function fetchMe(): Promise<UserOut> {
  return apiGet("/auth/me");
}

export function verifyEmail(token: string): Promise<{ message: string }> {
  return apiGet(`/auth/verify-email?token=${encodeURIComponent(token)}`);
}

export function resendVerification(email: string): Promise<{ message: string }> {
  return apiPost("/auth/verify-email/resend", { email });
}

export function forgotPassword(email: string): Promise<{ message: string }> {
  return apiPost("/auth/forgot-password", { email });
}

export function resetPassword(
  token: string,
  new_password: string,
  confirm_password: string
): Promise<{ message: string }> {
  return apiPost("/auth/reset-password", { token, new_password, confirm_password });
}

export function changePassword(
  current_password: string,
  new_password: string,
  confirm_password: string
): Promise<{ message: string }> {
  return apiPost("/auth/change-password", { current_password, new_password, confirm_password });
}
