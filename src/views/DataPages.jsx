"use client"

import { Download, Filter, Settings2 } from "lucide-react"
import { useApi } from "../hooks/useApi"

const money = (value) => `$${Number(value || 0).toLocaleString()}`

export function Transactions() {
  const { data, loading } = useApi("/transactions", [])
  return (
    <DataPage
      eyebrow="Ledger"
      title="Transactions"
      description="Posted income, card spend, transfers, recurring rules, tags, and notes."
      loading={loading}
      toolbar={<FilterButton />}
    >
      <DataTable rows={data} columns={["occurred_on", "type", "category", "amount", "recurring_rule", "notes"]} />
    </DataPage>
  )
}

export function Accounts() {
  const { data, loading } = useApi("/accounts", [])
  return (
    <DataPage
      eyebrow="Banking records"
      title="Accounts"
      description="Operating cash, bank balances, credit cards, investments, and loan exposure."
      loading={loading}
      toolbar={<FilterButton />}
    >
      <DataTable rows={data} columns={["name", "type", "institution", "opening_balance", "current_balance", "interest_rate"]} />
    </DataPage>
  )
}

export function Budgets() {
  const { data, loading } = useApi("/budgets", [])
  return (
    <DataPage
      eyebrow="Controls"
      title="Budgets"
      description="Category limits, actual spend, remaining headroom, and overspend risk."
      loading={loading}
      toolbar={<FilterButton />}
    >
      <DataTable rows={data} columns={["month", "category", "limit_amount", "spent", "remaining", "progress", "overspent"]} />
    </DataPage>
  )
}

export function Reports() {
  const { data, loading } = useApi("/analytics/summary", {})
  return (
    <DataPage
      eyebrow="Reporting"
      title="Reports"
      description="Compact banking summaries for accounting review, month-end planning, and exports."
      loading={loading}
      toolbar={
        <a
          className="btn btn-primary"
          href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/reports/export.csv`}
        >
          <Download size={13} /> Export CSV
        </a>
      }
    >
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="panel p-4">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              {key.replaceAll("_", " ")}
            </p>
            <p className="mt-1.5 text-lg font-bold text-slate-900">{String(value)}</p>
          </div>
        ))}
      </div>
    </DataPage>
  )
}

export function Settings() {
  const items = [
    ["Profile",       "Identity, contact, and workspace defaults."],
    ["Notifications", "Budget, debt, forecast, and admin alerts."],
    ["Security",      "Password, sessions, roles, and policy controls."],
    ["Integrations",  "Bank feeds, imports, exports, and accounting sync."],
  ]
  return (
    <DataPage
      eyebrow="Workspace"
      title="Settings"
      description="Banking workspace controls for people, policy, security, and data movement."
    >
      <div className="grid gap-3 md:grid-cols-2">
        {items.map(([label, text]) => (
          <button
            key={label}
            type="button"
            className="panel flex cursor-pointer items-start gap-3 p-4 text-left transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <Settings2 size={15} className="mt-0.5 shrink-0 text-blue-600" />
            <div>
              <p className="text-xs font-bold text-slate-900">{label}</p>
              <p className="small-copy mt-1">{text}</p>
            </div>
          </button>
        ))}
      </div>
    </DataPage>
  )
}

export function AdminPanel() {
  const { data, loading } = useApi("/admin/metrics", {})
  return (
    <DataPage eyebrow="Governance" title="Admin Panel" description="System usage, user governance, and operational banking metrics." loading={loading}>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="panel p-4">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{key.replaceAll("_", " ")}</p>
            <p className="mt-1.5 text-xl font-bold text-slate-900">{String(value)}</p>
          </div>
        ))}
      </div>
    </DataPage>
  )
}

/* ── Shared layout ─────────────────────────────────────────────────────── */

function DataPage({ eyebrow, title, description, loading, toolbar, children }) {
  return (
    <section className="space-y-4">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="page-title mt-1">{title}</h1>
          <p className="small-copy mt-1 max-w-2xl">{description}</p>
        </div>
        {toolbar && <div className="flex shrink-0 gap-2">{toolbar}</div>}
      </header>

      {loading ? (
        <p className="small-copy py-8 text-center">Loading…</p>
      ) : (
        children
      )}
    </section>
  )
}

function FilterButton() {
  return (
    <button type="button" className="btn btn-secondary">
      <Filter size={13} /> Filter
    </button>
  )
}

function DataTable({ rows, columns }) {
  return (
    <div className="panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="bank-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col.replaceAll("_", " ")}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                {columns.map((col) => (
                  <td key={col}>{formatCell(row, col)}</td>
                ))}
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <td colSpan={columns.length} className="py-8 text-center text-slate-400">
                  No records yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function formatCell(row, column) {
  const value = row[column]
  if (value === null || value === undefined || value === "") return <span className="text-slate-300">—</span>
  if (column.includes("amount") || column.includes("balance") || column === "spent" || column === "remaining") return money(value)
  if (column === "progress") return `${Number(value || 0).toFixed(1)}%`
  if (typeof value === "boolean") return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${value ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
      {value ? "Yes" : "No"}
    </span>
  )
  if (column.includes("status")) return (
    <span className="status-pill">{String(value)}</span>
  )
  return <span className="text-slate-700">{String(value)}</span>
}
