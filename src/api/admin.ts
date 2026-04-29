/**
 * Admin API — endpoints restricted to the "admin" role only.
 * Covers: platform metrics, user management, IAM (roles, permissions, policy decisions),
 *         risk alerts, compliance cases, ledger operations, audit logs, security events.
 *
 * IMPORTANT: These endpoints must only be called from admin-gated UI surfaces.
 * The ProtectedRoute component enforces this at the routing layer.
 */

import { httpClient, idempotencyHeaders } from "./client"

// ── Types ──────────────────────────────────────────────────────────────────
export interface AdminUser {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export interface IamRole {
  name: string
  description: string
}

export interface IamPermission {
  code: string
  description: string
}

export interface PolicyDecision {
  id: number
  permission: string
  decision: "allow" | "deny"
  user_id: number
  reason: string
  created_at: string
}

export interface RiskAlert {
  id: number
  severity: string
  status: string
  rule_code: string
  title: string
  transfer_id: number | null
  account_id: number | null
  created_at: string
}

export interface ComplianceCase {
  id: number
  case_number: string
  status: string
  alert_id: number
  assigned_to_user_id: number | null
  disposition: string | null
  created_at: string
  closed_at: string | null
}

export interface LedgerBalance {
  current_balance: number
  available_balance: number
  held_amount: number
}

export interface LedgerEntry {
  id: number
  effective_on: string
  direction: "debit" | "credit"
  event_type: string
  amount: number
  transfer_id: number | null
  transaction_id: number | null
  description: string | null
}

export interface LedgerHold {
  id: number
  transfer_id: number | null
  card_authorization_id: number | null
  amount: number
  status: string
  reason: string | null
  expires_at: string | null
  released_at: string | null
}

export interface AuditLog {
  id: number
  action: string
  actor_user_id: number
  resource_type: string
  resource_id: string | number | null
  outcome: string
  created_at: string
}

export interface SecurityEvent {
  id: number
  event_type: string
  severity: string
  user_id: number | null
  ip_address: string
  created_at: string
}

export interface AlertResolutionPayload {
  resolution_notes: string
}

// ── Platform metrics ───────────────────────────────────────────────────────
export async function getAdminMetrics(): Promise<Record<string, number | string>> {
  const { data } = await httpClient.get("/admin/metrics")
  return data
}

// ── User management ────────────────────────────────────────────────────────
export async function getUsers(): Promise<AdminUser[]> {
  const { data } = await httpClient.get<AdminUser[]>("/users")
  return data
}

// ── IAM ────────────────────────────────────────────────────────────────────
export async function getIamRoles(): Promise<IamRole[]> {
  const { data } = await httpClient.get<IamRole[]>("/iam/roles")
  return data
}

export async function getIamPermissions(): Promise<IamPermission[]> {
  const { data } = await httpClient.get<IamPermission[]>("/iam/permissions")
  return data
}

export async function getPolicyDecisions(): Promise<PolicyDecision[]> {
  const { data } = await httpClient.get<PolicyDecision[]>("/iam/policy-decisions")
  return data
}

export async function assignRole(userId: number, roleName: string): Promise<void> {
  await httpClient.post(
    "/iam/assign-role",
    { user_id: userId, role_name: roleName },
    idempotencyHeaders("assign-role"),
  )
}

// ── Risk alerts ────────────────────────────────────────────────────────────
export async function getRiskAlerts(): Promise<RiskAlert[]> {
  const { data } = await httpClient.get<RiskAlert[]>("/risk/alerts")
  return data
}

export async function resolveAlert(
  id: number,
  payload: AlertResolutionPayload,
): Promise<RiskAlert> {
  const { data } = await httpClient.post<RiskAlert>(
    `/risk/alerts/${id}/resolve`,
    payload,
    idempotencyHeaders(`resolve-alert-${id}`),
  )
  return data
}

export async function dismissAlert(
  id: number,
  payload: AlertResolutionPayload,
): Promise<RiskAlert> {
  const { data } = await httpClient.post<RiskAlert>(
    `/risk/alerts/${id}/dismiss`,
    payload,
    idempotencyHeaders(`dismiss-alert-${id}`),
  )
  return data
}

// ── Compliance ─────────────────────────────────────────────────────────────
export async function getComplianceCases(): Promise<ComplianceCase[]> {
  const { data } = await httpClient.get<ComplianceCase[]>("/compliance/cases")
  return data
}

// ── Ledger ─────────────────────────────────────────────────────────────────
export async function getLedgerBalance(accountId: number): Promise<LedgerBalance> {
  const { data } = await httpClient.get<LedgerBalance>(
    `/ledger/accounts/${accountId}/balance`,
  )
  return data
}

export async function getLedgerEntries(accountId: number): Promise<LedgerEntry[]> {
  const { data } = await httpClient.get<LedgerEntry[]>(
    `/ledger/accounts/${accountId}/entries`,
  )
  return data
}

export async function getLedgerHolds(accountId?: number): Promise<LedgerHold[]> {
  const url = accountId
    ? `/ledger/holds?account_id=${accountId}`
    : "/ledger/holds"
  const { data } = await httpClient.get<LedgerHold[]>(url)
  return data
}

export async function createLedgerSnapshot(accountId: number): Promise<void> {
  await httpClient.post(
    `/ledger/accounts/${accountId}/snapshot`,
    {},
    idempotencyHeaders(`snapshot-${accountId}`),
  )
}

// ── Audit & security ───────────────────────────────────────────────────────
export async function getAuditLogs(): Promise<AuditLog[]> {
  const { data } = await httpClient.get<AuditLog[]>("/admin/audit-logs")
  return data
}

export async function getSecurityEvents(): Promise<SecurityEvent[]> {
  const { data } = await httpClient.get<SecurityEvent[]>("/admin/security-events")
  return data
}
