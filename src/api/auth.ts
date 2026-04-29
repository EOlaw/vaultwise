/**
 * Authentication API — login, register, MFA, step-up, sessions.
 * Accessible by every role.
 */

import { httpClient, clearAuthStorage, idempotencyHeaders } from "./client"

// ── Types ──────────────────────────────────────────────────────────────────
export interface AuthUser {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  session_key: string
  user: AuthUser
}

export interface MfaDevice {
  id: number
  label: string
  device_type: string
  is_confirmed: boolean
  is_active: boolean
  last_used_at: string | null
}

export interface MfaSetupResponse {
  device_id: number
  secret: string
  totp_uri: string
}

export interface Session {
  session_key: string
  device_label: string
  ip_address: string
  trusted_device: boolean
  step_up_expires_at: string | null
  is_active: boolean
  last_seen_at: string
}

export interface StepUpPayload {
  password?: string
  mfa_code?: string
}

// ── Helpers ────────────────────────────────────────────────────────────────
function persist(tokens: AuthTokens): void {
  if (typeof window === "undefined") return
  localStorage.setItem("access_token", tokens.access_token)
  localStorage.setItem("refresh_token", tokens.refresh_token)
  localStorage.setItem("session_key", tokens.session_key)
  localStorage.setItem("user", JSON.stringify(tokens.user))
}

// ── Login ──────────────────────────────────────────────────────────────────
export async function login(
  email: string,
  password: string,
  mfa_code?: string,
): Promise<AuthTokens> {
  const { data } = await httpClient.post<AuthTokens>("/auth/login", {
    email,
    password,
    ...(mfa_code ? { mfa_code } : {}),
  })
  persist(data)
  return data
}

// ── Register ───────────────────────────────────────────────────────────────
export async function register(payload: {
  email: string
  password: string
  full_name: string
  role?: string
}): Promise<AuthTokens> {
  const { data } = await httpClient.post<AuthTokens>("/auth/register", payload)
  persist(data)
  return data
}

// ── Logout ─────────────────────────────────────────────────────────────────
export function logout(): void {
  clearAuthStorage()
}

// ── Step-up authentication ─────────────────────────────────────────────────
export async function stepUp(payload: StepUpPayload): Promise<{ step_up_expires_at: string }> {
  const { data } = await httpClient.post<{ step_up_expires_at: string }>(
    "/auth/step-up",
    payload,
  )
  if (typeof window !== "undefined") {
    localStorage.setItem("step_up_expires_at", data.step_up_expires_at)
  }
  return data
}

// ── MFA ────────────────────────────────────────────────────────────────────
export async function getMfaStatus(): Promise<{
  enabled: boolean
  devices: MfaDevice[]
}> {
  const { data } = await httpClient.get("/auth/mfa")
  return data
}

export async function setupMfa(label: string): Promise<MfaSetupResponse> {
  const { data } = await httpClient.post<MfaSetupResponse>("/auth/mfa/setup", { label })
  return data
}

export async function confirmMfa(deviceId: number, code: string): Promise<void> {
  await httpClient.post(`/auth/mfa/${deviceId}/confirm`, { code })
}

export async function removeMfaDevice(deviceId: number): Promise<void> {
  await httpClient.delete(`/auth/mfa/${deviceId}`)
}

// ── Sessions ───────────────────────────────────────────────────────────────
export async function getSessions(): Promise<Session[]> {
  const { data } = await httpClient.get<Session[]>("/auth/sessions")
  return data
}

export async function trustCurrentDevice(): Promise<void> {
  await httpClient.post(
    "/auth/sessions/current/trust",
    {},
    idempotencyHeaders("trust-device"),
  )
}

export async function revokeSession(sessionKey: string): Promise<void> {
  await httpClient.delete(`/auth/sessions/${sessionKey}`)
}
