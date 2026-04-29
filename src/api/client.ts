/**
 * Base HTTP client.
 *
 * Security notes:
 *  - Tokens are stored in localStorage (standard SPA approach).
 *    For higher-security requirements, migrate to httpOnly cookies server-side.
 *  - Tokens are NEVER logged or added to error messages.
 *  - The device fingerprint is a random UUID — it is not derived from hardware
 *    and carries no PII beyond browser user-agent (first 120 chars).
 */

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios"

// ── Constants ──────────────────────────────────────────────────────────────
const BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

const REQUEST_TIMEOUT_MS = 15_000

// ── Token helpers (never export raw token values) ──────────────────────────
function readStorage(key: string): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(key)
}

function writeStorage(key: string, value: string): void {
  if (typeof window !== "undefined") localStorage.setItem(key, value)
}

export function clearAuthStorage(): void {
  if (typeof window !== "undefined") localStorage.clear()
}

function getOrCreateFingerprint(): string {
  const existing = readStorage("device_fingerprint")
  if (existing) return existing
  const fresh = crypto.randomUUID()
  writeStorage("device_fingerprint", fresh)
  return fresh
}

// ── Axios instance ─────────────────────────────────────────────────────────
export const httpClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
})

// ── Request interceptor — attach bearer token + device headers ─────────────
httpClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window === "undefined") return config

    const token = readStorage("access_token")
    if (token) config.headers.Authorization = `Bearer ${token}`

    config.headers["X-Device-Fingerprint"] = getOrCreateFingerprint()
    config.headers["X-Device-Label"] = navigator.userAgent.slice(0, 120)

    return config
  },
  (error) => Promise.reject(error),
)

// ── Token-refresh queue ────────────────────────────────────────────────────
interface QueueEntry {
  resolve: (token: string) => void
  reject: (error: unknown) => void
}

let isRefreshing = false
let refreshQueue: QueueEntry[] = []

function drainQueue(error: unknown, token: string | null): void {
  refreshQueue.forEach((entry) =>
    error ? entry.reject(error) : entry.resolve(token!),
  )
  refreshQueue = []
}

// ── Response interceptor — silent token refresh on 401 ────────────────────
type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }

httpClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined

    if (!original || error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    original._retry = true

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        refreshQueue.push({ resolve, reject })
      }).then((newToken) => {
        original.headers.Authorization = `Bearer ${newToken}`
        return httpClient(original)
      })
    }

    isRefreshing = true
    const refreshToken = readStorage("refresh_token")

    if (!refreshToken) {
      clearAuthStorage()
      redirectToLogin()
      return Promise.reject(error)
    }

    try {
      // Use a plain axios call to avoid interceptor loops
      const { data } = await axios.post<{
        access_token: string
        refresh_token?: string
      }>(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken })

      writeStorage("access_token", data.access_token)
      if (data.refresh_token) writeStorage("refresh_token", data.refresh_token)

      drainQueue(null, data.access_token)
      original.headers.Authorization = `Bearer ${data.access_token}`
      return httpClient(original)
    } catch (refreshError) {
      drainQueue(refreshError, null)
      clearAuthStorage()
      redirectToLogin()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

function redirectToLogin(): void {
  if (typeof window !== "undefined") window.location.replace("/login")
}

// ── Idempotency helper ─────────────────────────────────────────────────────
/** Returns a header object with a unique Idempotency-Key for mutating calls. */
export function idempotencyHeaders(prefix = "req"): {
  headers: { "Idempotency-Key": string }
} {
  return { headers: { "Idempotency-Key": `${prefix}-${crypto.randomUUID()}` } }
}
