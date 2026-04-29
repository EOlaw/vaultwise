"use client"

import { useEffect, useState } from "react"
import { ArrowRight, BarChart3, LockKeyhole, ShieldCheck, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"

const FEATURES = [
  [ShieldCheck, "JWT access & refresh tokens", "Secure session management with automatic rotation"],
  [Users,       "Role-aware access controls",  "Admin, operator, approver, and viewer permissions"],
  [LockKeyhole, "Live dashboard records",       "Real-time balances, transactions, and analytics"],
]

export function AuthPages({ initialMode = "login" }) {
  const [mode, setMode] = useState(initialMode)
  const [form, setForm] = useState({ email: "", password: "", full_name: "", mfa_code: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const auth = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (auth.hydrated && auth.user) router.replace("/dashboard")
  }, [auth.hydrated, auth.user, router])

  async function submit(event) {
    event.preventDefault()
    setError("")
    setLoading(true)
    try {
      if (mode === "login") await auth.login(form.email, form.password, form.mfa_code)
      else await auth.register({ ...form, role: "user" })
      router.replace("/dashboard")
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const isLogin = mode === "login"

  return (
    <main className="grid min-h-screen bg-slate-50 p-3 lg:grid-cols-[1fr_0.92fr]">

      {/* ── Left panel – branding ── */}
      <section className="hidden overflow-hidden rounded-xl border border-slate-200 bg-slate-900 p-8 text-white lg:flex lg:flex-col lg:justify-between">
        <div>
          <div className="flex items-center gap-2.5 text-sm font-bold tracking-tight">
            <span className="grid size-8 place-items-center rounded-lg bg-white/10">
              <BarChart3 size={16} />
            </span>
            BankOS
          </div>
          <h1 className="mt-10 max-w-sm text-3xl font-extrabold leading-tight tracking-tight">
            Banking operations, visible in one secure workspace.
          </h1>
          <p className="mt-4 max-w-sm text-sm leading-6 text-white/60">
            Manage accounts, transactions, budget risk, reports, and liquidity signals.
          </p>
        </div>

        <div className="space-y-2.5">
          {FEATURES.map(([Icon, label, sub]) => (
            <div key={label} className="flex items-start gap-3 rounded-lg border border-white/10 bg-white/5 px-3.5 py-3">
              <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-md bg-white/10">
                <Icon size={13} className="text-white/80" />
              </span>
              <div>
                <p className="text-xs font-semibold text-white/90">{label}</p>
                <p className="mt-0.5 text-[11px] text-white/50">{sub}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Right panel – form ── */}
      <section className="grid place-items-center p-4">
        <div className="w-full max-w-sm">

          <div className="mb-6">
            <div className="grid size-9 place-items-center rounded-lg bg-slate-900 text-white">
              <BarChart3 size={17} />
            </div>
            <h2 className="mt-4 text-xl font-extrabold tracking-tight text-slate-900">
              {isLogin ? "Sign in" : "Create account"}
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              {isLogin ? "Access your banking workspace." : "Set up your banking workspace."}
            </p>
          </div>

          <form onSubmit={submit} className="panel space-y-3 p-5">
            {!isLogin && (
              <label className="block">
                <span className="mb-1.5 block text-[11px] font-semibold text-slate-500">Full name</span>
                <input
                  className="input"
                  placeholder="Jane Smith"
                  autoComplete="name"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                />
              </label>
            )}

            <label className="block">
              <span className="mb-1.5 block text-[11px] font-semibold text-slate-500">Email address</span>
              <input
                className="input"
                type="email"
                placeholder="you@company.com"
                autoComplete="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </label>

            <label className="block">
              <span className="mb-1.5 block text-[11px] font-semibold text-slate-500">Password</span>
              <input
                className="input"
                type="password"
                placeholder="••••••••"
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </label>

            {isLogin && (
              <label className="block">
                <span className="mb-1.5 block text-[11px] font-semibold text-slate-500">
                  Authenticator code <span className="font-normal text-slate-400">(if enabled)</span>
                </span>
                <input
                  className="input"
                  placeholder="000000"
                  inputMode="numeric"
                  maxLength={6}
                  value={form.mfa_code}
                  onChange={(e) => setForm({ ...form, mfa_code: e.target.value })}
                />
              </label>
            )}

            {error && (
              <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-700">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary mt-1 w-full disabled:opacity-60"
            >
              {loading ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
              {!loading && <ArrowRight size={14} />}
            </button>
          </form>

          <p className="mt-4 text-center text-xs text-slate-500">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              type="button"
              className="font-semibold text-blue-600 hover:underline"
              onClick={() => {
                const next = isLogin ? "register" : "login"
                setMode(next)
                router.push(`/${next}`)
              }}
            >
              {isLogin ? "Create one" : "Sign in"}
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}
