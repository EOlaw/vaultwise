"use client"

import {
  AlertTriangle,
  ArrowUpRight,
  BadgeCheck,
  Banknote,
  Building2,
  CheckCircle2,
  CreditCard,
  Eye,
  FileCheck2,
  Landmark,
  ListChecks,
  LockKeyhole,
  ReceiptText,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  Users,
  WalletCards,
} from "lucide-react"
import Link from "next/link"
import { BudgetBars, CashFlowChart, CategoryPie } from "../charts/DashboardCharts"
import { StatCard } from "../components/StatCard"
import { useAuth } from "../context/AuthContext"
import { useApi } from "../hooks/useApi"

const money = (value) => `$${Number(value || 0).toLocaleString()}`
const percent = (value) => `${Number(value || 0).toLocaleString()}%`

const ROLE_DASHBOARDS = {
  admin: {
    eyebrow: "Executive control",
    title: "Administrator Command Center",
    description: "System exposure, approvals, controls, liquidity, and audit pressure in one operating view.",
    accent: "violet",
    icon: ShieldCheck,
    href: "/admin",
    action: "Open Admin",
    stats: [
      ["Platform net worth", (s) => money(s.net_worth), "text-violet-700"],
      ["Cash flow", (s) => money(s.net_cash_flow), (s) => s.net_cash_flow >= 0 ? "text-mint" : "text-coral"],
      ["Health score", (s) => s.financial_health_score || 0, "text-ink"],
      ["Risk reserve", (s) => money(s.tax_estimate_placeholder), "text-gold"],
    ],
    focus: [
      ["Risk alerts", "6 open", "2 high priority", ShieldAlert, "/risk"],
      ["User access", "42 active", "8 privileged", Users, "/admin"],
      ["Ledger checks", "99.98%", "reconciled", FileCheck2, "/ledger"],
    ],
    tasks: [
      ["Review high-value wire controls", "Risk", "High"],
      ["Validate privileged account access", "IAM", "Due today"],
      ["Sign off ledger exception report", "Finance", "Open"],
    ],
    chartTitle: "Enterprise Cash Movement",
    chartNote: "Income and expense movement across the platform",
    sideTitle: "Control Posture",
    sideNote: "Budget, exposure, and cash pressure",
  },
  owner: {
    eyebrow: "Business owner",
    title: "Owner Financial Workspace",
    description: "Cash position, spend discipline, approvals, and business payment readiness.",
    accent: "sky",
    icon: Building2,
    href: "/organizations",
    action: "Manage Business",
    stats: [
      ["Business value", (s) => money(s.net_worth), "text-sky-700"],
      ["Net cash flow", (s) => money(s.net_cash_flow), (s) => s.net_cash_flow >= 0 ? "text-mint" : "text-coral"],
      ["Coverage", (s) => `${s.emergency_fund_coverage_months || 0} mo`, "text-ink"],
      ["Savings rate", (s) => percent(s.savings_rate), "text-mint"],
    ],
    focus: [
      ["Approvals", "4 pending", "2 over threshold", ListChecks, "/approvals"],
      ["Payees", "18 verified", "3 new this week", Users, "/payees"],
      ["Cards", "12 active", "1 limit review", CreditCard, "/cards"],
    ],
    tasks: [
      ["Approve payroll funding batch", "Payments", "Today"],
      ["Review contractor spend variance", "Budget", "Watch"],
      ["Confirm operating reserve target", "Treasury", "Open"],
    ],
    chartTitle: "Business Cash Runway",
    chartNote: "Operating income against committed outflows",
    sideTitle: "Spend Discipline",
    sideNote: "Budget usage and category mix",
  },
  operator: {
    eyebrow: "Operations desk",
    title: "Operator Execution Dashboard",
    description: "Transfers, payees, card events, and queued operational work.",
    accent: "blue",
    icon: Landmark,
    href: "/transfers",
    action: "Create Transfer",
    stats: [
      ["Available balance", (s) => money(s.net_worth), "text-blue-700"],
      ["Monthly burn", (s) => money(s.monthly_burn_rate), "text-ink"],
      ["Cash flow", (s) => money(s.net_cash_flow), (s) => s.net_cash_flow >= 0 ? "text-mint" : "text-coral"],
      ["Debt ratio", (s) => percent(s.debt_to_income_ratio), "text-gold"],
    ],
    focus: [
      ["Transfers", "11 queued", "3 need submit", Landmark, "/transfers"],
      ["Payees", "5 pending", "verification", Users, "/payees"],
      ["Disputes", "2 active", "1 awaiting docs", AlertTriangle, "/disputes"],
    ],
    tasks: [
      ["Submit approved vendor payments", "Transfer", "Ready"],
      ["Update ACH payee verification", "Payee", "Pending"],
      ["Issue replacement card request", "Cards", "Open"],
    ],
    chartTitle: "Daily Funding Flow",
    chartNote: "Cash movement available for operations",
    sideTitle: "Execution Queue",
    sideNote: "Budget and activity signals",
  },
  approver: {
    eyebrow: "Dual control",
    title: "Approver Review Desk",
    description: "Pending approvals, threshold exceptions, policy fit, and recent ledger activity.",
    accent: "amber",
    icon: ListChecks,
    href: "/approvals",
    action: "Review Queue",
    stats: [
      ["Pending value", (s) => money(s.monthly_burn_rate), "text-amber-700"],
      ["Policy score", (s) => s.financial_health_score || 0, "text-ink"],
      ["Coverage", (s) => `${s.emergency_fund_coverage_months || 0} mo`, "text-mint"],
      ["Debt ratio", (s) => percent(s.debt_to_income_ratio), "text-gold"],
    ],
    focus: [
      ["Awaiting decision", "7 items", "3 urgent", ListChecks, "/approvals"],
      ["Exceptions", "2 flagged", "policy mismatch", ShieldAlert, "/risk"],
      ["Recent wires", "5 posted", "last 24h", Landmark, "/transactions"],
    ],
    tasks: [
      ["Approve ACME supply wire", "Wire", "$24,800"],
      ["Reject duplicate ACH batch", "ACH", "Duplicate"],
      ["Review limit override request", "Policy", "Manager"],
    ],
    chartTitle: "Approval Exposure Trend",
    chartNote: "Cash movement context before decisions",
    sideTitle: "Decision Context",
    sideNote: "Category mix and budget pressure",
  },
  viewer: {
    eyebrow: "Read-only insight",
    title: "Viewer Finance Overview",
    description: "Balances, trends, spend mix, and recent ledger activity without transaction controls.",
    accent: "emerald",
    icon: Eye,
    href: "/reports",
    action: "View Reports",
    stats: [
      ["Net worth", (s) => money(s.net_worth), "text-emerald-700"],
      ["Cash flow", (s) => money(s.net_cash_flow), (s) => s.net_cash_flow >= 0 ? "text-mint" : "text-coral"],
      ["Savings rate", (s) => percent(s.savings_rate), "text-mint"],
      ["Monthly burn", (s) => money(s.monthly_burn_rate), "text-ink"],
    ],
    focus: [
      ["Statements", "Current", "ready", FileCheck2, "/statements"],
      ["Reports", "12 saved", "3 shared", ReceiptText, "/reports"],
      ["Security", "Trusted", "MFA enabled", LockKeyhole, "/security-center"],
    ],
    tasks: [
      ["Read April cash report", "Report", "Ready"],
      ["Check category variance", "Analytics", "New"],
      ["Download current statement", "Statement", "Ready"],
    ],
    chartTitle: "Financial Trend",
    chartNote: "Income, expenses, and current trendline",
    sideTitle: "Read-only Signals",
    sideNote: "Spending mix and recent movement",
  },
  user: {
    eyebrow: "Customer banking",
    title: "Customer Finance Dashboard",
    description: "Balances, card access, statements, spending activity, and account security in one customer workspace.",
    accent: "emerald",
    icon: WalletCards,
    href: "/cards",
    action: "Manage Cards",
    stats: [
      ["Net worth", (s) => money(s.net_worth), "text-emerald-700"],
      ["Cash flow", (s) => money(s.net_cash_flow), (s) => s.net_cash_flow >= 0 ? "text-mint" : "text-coral"],
      ["Savings rate", (s) => percent(s.savings_rate), "text-mint"],
      ["Monthly burn", (s) => money(s.monthly_burn_rate), "text-ink"],
    ],
    focus: [
      ["Cards", "Manage", "turn on/off, limits, controls", CreditCard, "/cards"],
      ["Accounts", "Balances", "checking, savings, credit", WalletCards, "/accounts"],
      ["Statements", "Current", "download and review", FileCheck2, "/statements"],
    ],
    tasks: [
      ["Review Avery Everyday Debit", "Card", "Active"],
      ["Check latest posted card spend", "Transactions", "New"],
      ["Confirm account security settings", "Security", "Ready"],
    ],
    chartTitle: "Customer Cash Trend",
    chartNote: "Income and expense movement across your accounts",
    sideTitle: "Spending Signals",
    sideNote: "Budget and card activity signals",
  },
}

const accentClasses = {
  violet: {
    band: "border-violet-200 bg-violet-50",
    icon: "bg-violet-700 text-white",
    text: "text-violet-900",
    muted: "text-violet-700",
    button: "bg-violet-700 text-white hover:bg-violet-800",
    soft: "bg-violet-100 text-violet-800",
  },
  sky: {
    band: "border-sky-200 bg-sky-50",
    icon: "bg-sky-700 text-white",
    text: "text-sky-900",
    muted: "text-sky-700",
    button: "bg-sky-700 text-white hover:bg-sky-800",
    soft: "bg-sky-100 text-sky-800",
  },
  blue: {
    band: "border-blue-200 bg-blue-50",
    icon: "bg-blue-700 text-white",
    text: "text-blue-900",
    muted: "text-blue-700",
    button: "bg-blue-700 text-white hover:bg-blue-800",
    soft: "bg-blue-100 text-blue-800",
  },
  amber: {
    band: "border-amber-200 bg-amber-50",
    icon: "bg-amber-600 text-white",
    text: "text-amber-900",
    muted: "text-amber-700",
    button: "bg-amber-600 text-white hover:bg-amber-700",
    soft: "bg-amber-100 text-amber-800",
  },
  emerald: {
    band: "border-emerald-200 bg-emerald-50",
    icon: "bg-emerald-700 text-white",
    text: "text-emerald-900",
    muted: "text-emerald-700",
    button: "bg-emerald-700 text-white hover:bg-emerald-800",
    soft: "bg-emerald-100 text-emerald-800",
  },
}

export function Dashboard() {
  const { user } = useAuth()
  const { data, loading, error } = useApi("/dashboard", {
    summary: {},
    monthly_cash_flow: [],
    spending_by_category: [],
    budget_progress: [],
    recent_transactions: [],
    top_expenses: [],
    cash_flow_forecast: [],
  })

  if (loading) return <p className="small-copy">Loading banking dashboard...</p>
  if (error) return <p className="rounded-md bg-red-50 p-3 text-xs font-bold text-red-700">{error}</p>

  const s = data.summary || {}
  const role = user?.role || "viewer"
  const config = ROLE_DASHBOARDS[role] || ROLE_DASHBOARDS.viewer
  const accent = accentClasses[config.accent]

  return (
    <div className="space-y-3">
      <header className="flex flex-col justify-between gap-3 xl:flex-row xl:items-end">
        <div className="min-w-0">
          <p className="eyebrow">{config.eyebrow}</p>
          <h1 className="page-title mt-1">{config.title}</h1>
          <p className="small-copy mt-1 max-w-3xl">{config.description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="status-pill">Health {s.financial_health_score || 0}</span>
          <span className="status-pill">Generated {data.generated_on || "today"}</span>
          <span className={`inline-flex items-center rounded-full px-2 py-1 text-[11px] font-black uppercase ${accent.soft}`}>
            {role}
          </span>
        </div>
      </header>

      <RoleHero config={config} accent={accent} user={user} />

      <section className="stat-grid">
        {config.stats.map(([label, resolveValue, resolveAccent]) => (
          <StatCard
            key={label}
            label={label}
            value={resolveValue(s)}
            accent={typeof resolveAccent === "function" ? resolveAccent(s) : resolveAccent}
          />
        ))}
      </section>

      <section className="grid gap-3 xl:grid-cols-[1.45fr_0.95fr]">
        <div className="panel p-3">
          <ChartHeader title={config.chartTitle} note={config.chartNote} />
          <CashFlowChart data={data.monthly_cash_flow} />
        </div>
        <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
          {config.focus.map(([title, value, note, Icon, href]) => (
            <FocusCard key={title} title={title} value={value} note={note} icon={Icon} href={href} accent={accent} />
          ))}
        </div>
      </section>

      <section className="grid gap-3 xl:grid-cols-[0.9fr_0.9fr_1.1fr]">
        <div className="panel p-3">
          <ChartHeader title={config.sideTitle} note="Category allocation" />
          <CategoryPie data={data.spending_by_category} />
        </div>
        <div className="panel p-3">
          <ChartHeader title="Budget Pressure" note={config.sideNote} />
          <BudgetBars data={data.budget_progress} />
        </div>
        <TaskPanel rows={config.tasks} accent={accent} />
      </section>

      <section className="grid gap-3 xl:grid-cols-[1.1fr_0.9fr]">
        <RecentActivity rows={data.recent_transactions || []} role={role} />
        <ListPanel
          icon={role === "approver" ? BadgeCheck : role === "operator" ? Banknote : ReceiptText}
          title={role === "admin" ? "Top Platform Expenses" : "Priority Financial Items"}
          rows={(data.top_expenses || []).slice(0, 6).map((item) => [item.category, money(item.amount)])}
        />
      </section>
    </div>
  )
}

function RoleHero({ config, accent, user }) {
  const Icon = config.icon
  return (
    <section className={`flex flex-col justify-between gap-3 rounded-lg border px-3 py-3 sm:flex-row sm:items-center ${accent.band}`}>
      <div className="flex min-w-0 items-center gap-3">
        <span className={`grid size-9 shrink-0 place-items-center rounded-md ${accent.icon}`}>
          <Icon size={17} />
        </span>
        <div className="min-w-0">
          <p className={`truncate text-xs font-black ${accent.text}`}>{user?.full_name || "Workspace user"}</p>
          <p className={`mt-0.5 text-[11px] leading-4 ${accent.muted}`}>{config.description}</p>
        </div>
      </div>
      <Link href={config.href} className={`inline-flex shrink-0 items-center justify-center gap-1 rounded-md px-3 py-2 text-[11px] font-black transition ${accent.button}`}>
        {config.action} <ArrowUpRight size={12} />
      </Link>
    </section>
  )
}

function FocusCard({ title, value, note, icon: Icon, href, accent }) {
  return (
    <Link href={href} className="panel flex min-h-[84px] items-start justify-between gap-3 p-3 transition hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(20,35,31,0.08)]">
      <div className="min-w-0">
        <p className="truncate text-[11px] font-black uppercase tracking-wide text-slate-500">{title}</p>
        <p className="mt-1 text-base font-black leading-tight text-ink">{value}</p>
        <p className="mt-1 truncate text-[11px] text-slate-500">{note}</p>
      </div>
      <span className={`grid size-8 shrink-0 place-items-center rounded-md ${accent.soft}`}>
        <Icon size={15} />
      </span>
    </Link>
  )
}

function TaskPanel({ rows, accent }) {
  return (
    <div className="panel p-3">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 className="section-title">Role Work Queue</h2>
          <p className="small-copy">Compact action list for the current access level</p>
        </div>
        <CheckCircle2 size={15} className={accent.muted} />
      </div>
      <div className="space-y-2">
        {rows.map(([label, type, status]) => (
          <div key={label} className="grid grid-cols-[1fr_auto] gap-2 rounded-md border border-line px-3 py-2 text-xs">
            <div className="min-w-0">
              <p className="truncate font-black text-ink">{label}</p>
              <p className="mt-0.5 text-[11px] text-slate-500">{type}</p>
            </div>
            <span className={`self-center rounded-full px-2 py-1 text-[10px] font-black uppercase ${accent.soft}`}>{status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function RecentActivity({ rows, role }) {
  return (
    <div className="panel p-3">
      <ChartHeader title={role === "approver" ? "Decision Ledger" : "Recent Transactions"} note="Latest account activity" />
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {rows.slice(0, 8).map((t) => (
          <div key={t.id} className="flex min-w-0 items-center justify-between gap-3 rounded-md border border-line px-3 py-2 text-xs">
            <div className="min-w-0">
              <p className="truncate font-black">{t.category}</p>
              <p className="text-[11px] text-slate-500">{t.occurred_on}</p>
            </div>
            <b className={`shrink-0 ${t.type === "income" ? "text-mint" : "text-ink"}`}>{money(t.amount)}</b>
          </div>
        ))}
        {!rows.length ? <p className="small-copy">No activity yet.</p> : null}
      </div>
    </div>
  )
}

function ChartHeader({ title, note }) {
  return (
    <div className="mb-3 flex items-start justify-between gap-3">
      <div className="min-w-0">
        <h2 className="section-title truncate">{title}</h2>
        <p className="small-copy">{note}</p>
      </div>
      <TrendingUp size={15} className="shrink-0 text-slate-400" />
    </div>
  )
}

function ListPanel({ icon: Icon, title, rows }) {
  return (
    <div className="panel p-3">
      <div className="mb-3 flex items-center gap-2">
        <Icon size={16} className="text-mint" />
        <h2 className="section-title">{title}</h2>
      </div>
      <div className="space-y-2">
        {rows.length ? rows.map(([label, value], i) => (
          <div className="flex justify-between gap-3 rounded-md border border-line px-3 py-2 text-xs" key={`${i}-${label}-${value}`}>
            <span className="min-w-0 truncate font-bold text-slate-600">{label}</span>
            <b className="shrink-0">{value}</b>
          </div>
        )) : <p className="small-copy">No records yet.</p>}
      </div>
    </div>
  )
}
