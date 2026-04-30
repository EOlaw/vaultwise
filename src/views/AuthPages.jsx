"use client"

import { useEffect, useState } from "react"
import {
  ArrowRight, Award, CheckCircle2, CreditCard, Landmark,
  LineChart, LockKeyhole, PiggyBank, Shield, ShieldCheck,
  Users, WalletCards
} from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"

const loginFeatures = [
  [WalletCards,  "All your accounts in one place",    "Checking, savings, cards, loans, and investments — connected."],
  [ShieldCheck,  "Bank-grade security",               "MFA, step-up authentication, and trusted device tracking."],
  [LineChart,    "Real-time financial insights",      "Balances, budgets, cash flow, and risk signals — live."],
  [Users,        "Team and business controls",        "Role-aware access, dual-control approvals, and audit trails."],
]

const registerBenefits = [
  "Free checking with no monthly fee",
  "High-yield savings with competitive APY",
  "Virtual and physical card issuing",
  "Mobile deposits and instant transfers",
  "Business banking and team controls",
  "24/7 fraud monitoring and alerts",
]

export function AuthPages({ initialMode = "login" }) {
  const [mode, setMode] = useState(initialMode)
  const [form, setForm] = useState({ email: "", password: "", full_name: "", mfa_code: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showMfa, setShowMfa] = useState(false)
  const auth = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (auth.hydrated && auth.user) router.replace("/dashboard")
  }, [auth.hydrated, auth.user, router])

  function set(field) {
    return (e) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }))
      setError("")
    }
  }

  async function submit(e) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      if (mode === "login") {
        await auth.login(form.email, form.password, form.mfa_code)
      } else {
        await auth.register({ ...form, role: "user" })
      }
      router.replace("/dashboard")
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Something went wrong."
      if (msg.toLowerCase().includes("mfa") || msg.toLowerCase().includes("authenticator")) {
        setShowMfa(true)
      }
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const isLogin = mode === "login"

  return (
    <div className="auth-shell">
      {/* Top bar */}
      <header className="auth-topbar">
        <a href="/" className="auth-topbar-brand">
          <span className="auth-topbar-mark"><Landmark size={17} /></span>
          <span>VaultWise</span>
        </a>
        <nav className="auth-topbar-nav">
          <a href="/">Home</a>
          <a href="/product">Products</a>
          <a href="/pricing">Pricing</a>
          <a href="/security">Security</a>
        </nav>
        <div className="auth-topbar-actions">
          <span className="auth-topbar-fdic"><Shield size={11} /> FDIC Insured</span>
          <a href="/contact" className="auth-topbar-help">Need help?</a>
        </div>
      </header>

      <main className="auth-main">
        {/* Left panel */}
        <aside className="auth-left-panel">
          <div className="auth-left-inner">
            {isLogin ? (
              <>
                <p className="auth-left-eyebrow">Secure online banking</p>
                <h2 className="auth-left-heading">
                  Everything you need to manage your money — all in one place.
                </h2>
                <p className="auth-left-sub">
                  Sign in to access your accounts, cards, transfers, and financial insights across all of your VaultWise products.
                </p>
                <div className="auth-left-features">
                  {loginFeatures.map(([Icon, label, sub]) => (
                    <div key={label} className="auth-left-feature">
                      <span className="auth-left-feature-icon"><Icon size={16} /></span>
                      <div>
                        <strong>{label}</strong>
                        <span>{sub}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <>
                <p className="auth-left-eyebrow">Join VaultWise</p>
                <h2 className="auth-left-heading">
                  Open your account in minutes. Bank better starting today.
                </h2>
                <p className="auth-left-sub">
                  VaultWise gives you the tools to manage personal and business finances from a single, secure workspace.
                </p>
                <div className="auth-left-benefits">
                  {registerBenefits.map((item) => (
                    <div key={item} className="auth-left-benefit">
                      <CheckCircle2 size={16} />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                <div className="auth-left-certs">
                  <span><Shield size={12} /> FDIC Insured</span>
                  <span><Award size={12} /> SOC 2 Type II</span>
                  <span><ShieldCheck size={12} /> PCI DSS L1</span>
                </div>
              </>
            )}
          </div>
          <div className="auth-left-card">
            <AuthPreviewCard isLogin={isLogin} />
          </div>
        </aside>

        {/* Right panel — form */}
        <section className="auth-right-panel">
          <div className="auth-form-wrap">

            {/* Mode toggle tabs */}
            <div className="auth-tabs">
              <button
                type="button"
                className={isLogin ? "auth-tab active" : "auth-tab"}
                onClick={() => { setMode("login"); setError(""); setShowMfa(false); router.push("/login") }}
              >
                Sign in
              </button>
              <button
                type="button"
                className={!isLogin ? "auth-tab active" : "auth-tab"}
                onClick={() => { setMode("register"); setError(""); setShowMfa(false); router.push("/register") }}
              >
                Open account
              </button>
            </div>

            <form onSubmit={submit} className="auth-form" noValidate>

              {!isLogin && (
                <div className="auth-field">
                  <label htmlFor="auth-name">Full name</label>
                  <input
                    id="auth-name"
                    type="text"
                    placeholder="Jane Smith"
                    autoComplete="name"
                    value={form.full_name}
                    onChange={set("full_name")}
                    required
                  />
                </div>
              )}

              <div className="auth-field">
                <label htmlFor="auth-email">{isLogin ? "Username / Email" : "Email address"}</label>
                <input
                  id="auth-email"
                  type="email"
                  placeholder="you@company.com"
                  autoComplete="email"
                  value={form.email}
                  onChange={set("email")}
                  required
                />
              </div>

              <div className="auth-field">
                <div className="auth-field-row">
                  <label htmlFor="auth-password">Password</label>
                  {isLogin && <a href="#" className="auth-forgot">Forgot password?</a>}
                </div>
                <input
                  id="auth-password"
                  type="password"
                  placeholder="••••••••"
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  value={form.password}
                  onChange={set("password")}
                  required
                />
              </div>

              {(isLogin && showMfa) && (
                <div className="auth-field">
                  <label htmlFor="auth-mfa">Authenticator code</label>
                  <input
                    id="auth-mfa"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    placeholder="000000"
                    value={form.mfa_code}
                    onChange={set("mfa_code")}
                    autoFocus
                  />
                  <span className="auth-field-hint">Enter the 6-digit code from your authenticator app.</span>
                </div>
              )}

              {error && (
                <div className="auth-error" role="alert">
                  <LockKeyhole size={14} />
                  <span>{error}</span>
                </div>
              )}

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading
                  ? <span className="auth-spinner" />
                  : isLogin ? "Sign in" : "Create account"
                }
                {!loading && <ArrowRight size={15} />}
              </button>

              {isLogin && (
                <label className="auth-remember">
                  <input type="checkbox" />
                  Keep me signed in on this device
                </label>
              )}

            </form>

            <div className="auth-form-footer">
              {isLogin ? (
                <p>
                  Not enrolled?{" "}
                  <button type="button" onClick={() => { setMode("register"); setError(""); router.push("/register") }}>
                    Open a free account
                  </button>
                </p>
              ) : (
                <p>
                  Already have an account?{" "}
                  <button type="button" onClick={() => { setMode("login"); setError(""); router.push("/login") }}>
                    Sign in
                  </button>
                </p>
              )}
              <p className="auth-legal">
                By continuing, you agree to VaultWise's{" "}
                <a href="#">Terms of Use</a> and <a href="#">Privacy Policy</a>.
              </p>
            </div>

          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="auth-footer">
        <div className="auth-footer-inner">
          <span>© 2025 VaultWise Financial Technologies, Inc.</span>
          <div className="auth-footer-links">
            <a href="#">Privacy</a>
            <a href="#">Security</a>
            <a href="#">Terms</a>
            <a href="/contact">Contact</a>
          </div>
          <span className="auth-footer-fdic"><Shield size={11} /> Member FDIC · Equal Housing Lender</span>
        </div>
      </footer>
    </div>
  )
}

function AuthPreviewCard({ isLogin }) {
  if (isLogin) {
    return (
      <div className="auth-preview-card">
        <div className="auth-preview-header">
          <div>
            <p className="auth-preview-kicker">My accounts</p>
            <h3>Account overview</h3>
          </div>
          <span className="auth-preview-live">Live</span>
        </div>
        <div className="auth-preview-accounts">
          <AuthPreviewAccount icon={WalletCards} label="Primary Checking" balance="$12,480.22" tag="Active" />
          <AuthPreviewAccount icon={PiggyBank} label="High-Yield Savings" balance="$8,250.00" tag="+2.4% APY" />
          <AuthPreviewAccount icon={CreditCard} label="Business Visa •• 4829" balance="$3,210.00" tag="Virtual" />
        </div>
        <div className="auth-preview-footer">
          <span>Last updated</span>
          <strong>Just now</strong>
        </div>
      </div>
    )
  }
  return (
    <div className="auth-preview-card">
      <div className="auth-preview-header">
        <div>
          <p className="auth-preview-kicker">Getting started</p>
          <h3>Open in 3 minutes</h3>
        </div>
        <CheckCircle2 size={18} style={{ color: "#4ade80" }} />
      </div>
      <div className="auth-preview-steps">
        {[
          ["01", "Create account", "Email, password, and your name"],
          ["02", "Verify identity", "Quick identity confirmation"],
          ["03", "Fund & go", "Connect a bank or make a deposit"],
        ].map(([num, title, sub]) => (
          <div key={num} className="auth-preview-step">
            <span className="auth-preview-num">{num}</span>
            <div>
              <strong>{title}</strong>
              <span>{sub}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="auth-preview-footer">
        <span>No minimum balance required</span>
        <strong>Free forever</strong>
      </div>
    </div>
  )
}

function AuthPreviewAccount({ icon: Icon, label, balance, tag }) {
  return (
    <div className="auth-preview-account">
      <span className="auth-preview-account-icon"><Icon size={16} /></span>
      <div className="auth-preview-account-info">
        <strong>{label}</strong>
        <span>{balance}</span>
      </div>
      <span className="auth-preview-account-tag">{tag}</span>
    </div>
  )
}
