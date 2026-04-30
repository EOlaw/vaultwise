"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"

export function HomeSignInPanel() {
  const [form, setForm] = useState({ email: "", password: "", remember: false })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const auth = useAuth()
  const router = useRouter()

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.email || !form.password) {
      setError("Please enter your username and password.")
      return
    }
    setError("")
    setLoading(true)
    try {
      await auth.login(form.email, form.password)
      router.replace("/dashboard")
    } catch (err) {
      setError(err.response?.data?.detail || "Sign in failed. Please check your credentials.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="chase-signin-panel" aria-label="Account sign in">
      <h2>Welcome back</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Username / Email
          <input
            type="email"
            name="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
        </label>
        <label className="chase-check">
          <input
            type="checkbox"
            checked={form.remember}
            onChange={(e) => setForm({ ...form, remember: e.target.checked })}
          />
          Remember username
        </label>

        {error && <p className="chase-signin-error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <div className="chase-signin-links">
        <a href="/login">Forgot username / password?</a>
        <a href="/register">Not enrolled? Sign up now.</a>
      </div>
    </aside>
  )
}
