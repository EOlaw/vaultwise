"use client"

import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { httpClient as api } from "../api/client.ts"

const AuthContext = createContext(null)

function storedUser() {
  if (typeof window === "undefined") return null
  try {
    return JSON.parse(localStorage.getItem("user") || "null")
  } catch {
    localStorage.removeItem("user")
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setUser(storedUser())
    setHydrated(true)
  }, [])

  async function login(email, password, mfa_code = "") {
    const { data } = await api.post("/auth/login", { email, password, mfa_code: mfa_code || undefined })
    if (typeof window === "undefined") return
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    localStorage.setItem("session_key", data.session_key || "")
    localStorage.setItem("user", JSON.stringify(data.user))
    setUser(data.user)
  }

  async function register(payload) {
    const { data } = await api.post("/auth/register", payload)
    if (typeof window === "undefined") return
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    localStorage.setItem("session_key", data.session_key || "")
    localStorage.setItem("user", JSON.stringify(data.user))
    setUser(data.user)
  }

  async function stepUp(payload) {
    const { data } = await api.post("/auth/step-up", payload)
    if (typeof window !== "undefined") localStorage.setItem("step_up_expires_at", data.step_up_expires_at)
    return data
  }

  async function trustDevice() {
    const { data } = await api.post("/auth/sessions/current/trust")
    return data
  }

  function logout() {
    if (typeof window === "undefined") return
    localStorage.clear()
    setUser(null)
  }

  const value = useMemo(() => ({ user, hydrated, login, register, logout, stepUp, trustDevice }), [hydrated, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
