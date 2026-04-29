/**
 * Shared API — endpoints every authenticated role can call.
 * Includes: dashboard summary, notifications, analytics summary, reports export.
 */

import { httpClient, idempotencyHeaders } from "./client"

// ── Types ──────────────────────────────────────────────────────────────────
export interface DashboardSummary {
  net_worth: number
  net_cash_flow: number
  savings_rate: number
  monthly_burn_rate: number
  debt_to_income_ratio: number
  emergency_fund_coverage_months: number
  tax_estimate_placeholder: number
  financial_health_score: number
}

export interface CashFlowPoint {
  month: string
  income: number
  expenses: number
}

export interface SpendingCategory {
  category: string
  amount: number
  percentage: number
}

export interface BudgetProgress {
  category: string
  limit_amount: number
  spent: number
  progress: number
}

export interface RecentTransaction {
  id: number
  category: string
  occurred_on: string
  amount: number
  type: "income" | "expense" | "transfer"
}

export interface DashboardData {
  summary: DashboardSummary
  monthly_cash_flow: CashFlowPoint[]
  spending_by_category: SpendingCategory[]
  budget_progress: BudgetProgress[]
  recent_transactions: RecentTransaction[]
  top_expenses: { category: string; amount: number }[]
  cash_flow_forecast: number[]
  generated_on: string
}

export interface Notification {
  id: number
  priority: string
  notification_type: string
  title: string
  body: string
  read_at: string | null
  created_at: string
}

export interface AnalyticsSummary {
  total_income: number
  total_expenses: number
  net_cash_flow: number
  savings_rate: number
  average_monthly_spend: number
  transaction_count: number
}

// ── Dashboard ──────────────────────────────────────────────────────────────
export async function getDashboard(): Promise<DashboardData> {
  const { data } = await httpClient.get<DashboardData>("/dashboard")
  return data
}

// ── Notifications ──────────────────────────────────────────────────────────
export async function getNotifications(): Promise<Notification[]> {
  const { data } = await httpClient.get<Notification[]>("/notifications")
  return data
}

export async function markNotificationRead(id: number): Promise<void> {
  await httpClient.post(
    `/notifications/${id}/read`,
    {},
    idempotencyHeaders("notif-read"),
  )
}

export async function markAllNotificationsRead(): Promise<void> {
  await httpClient.post(
    "/notifications/read-all",
    {},
    idempotencyHeaders("notif-read-all"),
  )
}

// ── Analytics summary (read-only — safe for all roles) ────────────────────
export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const { data } = await httpClient.get<AnalyticsSummary>("/analytics/summary")
  return data
}

// ── Reports export URL (no token in URL — server reads Authorization header) ─
export function getReportExportUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  return `${base}/reports/export.csv`
}
