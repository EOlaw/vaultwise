"use client"

import {
  BarChart3,
  Bell,
  Building2,
  Calculator,
  CreditCard,
  FileCheck2,
  FileText,
  Landmark,
  LayoutDashboard,
  ListChecks,
  LogOut,
  PieChart,
  Scale,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Siren,
  Sparkles,
  UserPlus,
  WalletCards,
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"
import { ROLE_PAGES } from "../lib/roles"
import { pagePaths } from "../utils/routes"

// ── Navigation master list — order controls sidebar order ──────────────────
const ALL_NAV = [
  ["Dashboard",     "dashboard",     LayoutDashboard],
  ["Transactions",  "transactions",  CreditCard],
  ["Accounts",      "accounts",      WalletCards],
  ["Business",      "organizations", Building2],
  ["Payees",        "payees",        UserPlus],
  ["Transfers",     "transfers",     Landmark],
  ["Approvals",     "approvals",     ListChecks],
  ["Risk",          "risk",          ShieldAlert],
  ["Ledger",        "ledger",        Scale],
  ["Statements",    "statements",    FileCheck2],
  ["Cards",         "cards",         CreditCard],
  ["Disputes",      "disputes",      Siren],
  ["Notifications", "notifications", Bell],
  ["Budgets",       "budgets",       PieChart],
  ["Analytics",     "analytics",     Calculator],
  ["Reports",       "reports",       FileText],
  ["Security",      "securityCenter",Shield],
  ["Settings",      "settings",      Settings],
  ["Admin",         "admin",         ShieldCheck],
]

// ── Visual theme per role ──────────────────────────────────────────────────
// Page sets come from lib/roles.ts (single source of truth).
const ROLE_STYLE = {
  admin: {
    label:         "Administrator",
    accentColor:   "#6d28d9",
    badgeClass:    "bg-violet-100 text-violet-800",
    activeClass:   "bg-violet-700 text-white",
    inactiveClass: "text-slate-600 hover:bg-violet-50 hover:text-violet-700",
  },
  operator: {
    label:         "Operator",
    accentColor:   "#1d4ed8",
    badgeClass:    "bg-blue-100 text-blue-800",
    activeClass:   "bg-blue-700 text-white",
    inactiveClass: "text-slate-600 hover:bg-blue-50 hover:text-blue-700",
  },
  owner: {
    label:         "Owner",
    accentColor:   "#0369a1",
    badgeClass:    "bg-sky-100 text-sky-800",
    activeClass:   "bg-sky-700 text-white",
    inactiveClass: "text-slate-600 hover:bg-sky-50 hover:text-sky-700",
  },
  approver: {
    label:         "Approver",
    accentColor:   "#d97706",
    badgeClass:    "bg-amber-100 text-amber-800",
    activeClass:   "bg-amber-600 text-white",
    inactiveClass: "text-slate-600 hover:bg-amber-50 hover:text-amber-700",
  },
  viewer: {
    label:         "Viewer",
    accentColor:   "#16a34a",
    badgeClass:    "bg-emerald-100 text-emerald-800",
    activeClass:   "bg-slate-900 text-white",
    inactiveClass: "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
  },
  user: {
    label:         "Customer",
    accentColor:   "#16a34a",
    badgeClass:    "bg-emerald-100 text-emerald-800",
    activeClass:   "bg-slate-900 text-white",
    inactiveClass: "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
  },
}

const FALLBACK_STYLE = ROLE_STYLE.viewer

function getRoleStyle(role) {
  return ROLE_STYLE[role] ?? FALLBACK_STYLE
}

function getRolePages(role) {
  return ROLE_PAGES[role] ?? ROLE_PAGES.user
}

// ── Component ──────────────────────────────────────────────────────────────
export function AppLayout({ page, children }) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const style   = getRoleStyle(user?.role)
  const allowed = getRolePages(user?.role)
  const visibleNav = ALL_NAV.filter(([, key]) => allowed.has(key))

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        {/* Role accent stripe */}
        <div style={{ height: 3, background: style.accentColor }} />

        <div className="flex items-center justify-between gap-3 px-4 py-3 lg:block">
          <Link href="/dashboard" className="sidebar-brand">
            <span className="sidebar-brand-mark"><BarChart3 size={17} /></span>
            BankOS
          </Link>

          <div className="workspace-card">
            <p className="workspace-meta"><Sparkles size={11} /> Workspace</p>
            <p className="mt-1.5 truncate text-xs font-bold text-slate-800">{user?.full_name}</p>
            <span className={`mt-2 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${style.badgeClass}`}>
              {style.label}
            </span>
          </div>

          <button
            className="btn btn-secondary lg:hidden"
            onClick={() => { logout(); router.push("/login") }}
          >
            <LogOut size={15} />
          </button>
        </div>

        <nav className="nav-scroll">
          {visibleNav.map(([label, key, Icon]) => (
            <Link
              key={key}
              href={pagePaths[key]}
              className={`side-nav-link ${
                page === key
                  ? `side-nav-link-active ${style.activeClass}`
                  : style.inactiveClass
              }`}
            >
              <span className="side-nav-icon"><Icon size={15} /></span>
              <span className="side-nav-label">{label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            className="btn w-full justify-start text-slate-600 hover:bg-slate-50"
            onClick={() => { logout(); router.push("/login") }}
          >
            <LogOut size={15} /> Sign out
          </button>
        </div>
      </aside>

      <main className="content-shell">
        <div className="content-inner">{children}</div>
      </main>
    </div>
  )
}
