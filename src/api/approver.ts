/**
 * Approver API — endpoints for the "approver" role.
 * Covers: approval queue (view, approve, reject) and approval policies.
 *
 * Requires step-up authentication for approve/reject mutations.
 */

import { httpClient, idempotencyHeaders } from "./client"

// ── Types ──────────────────────────────────────────────────────────────────
export interface Approval {
  id: number
  transfer_id: number
  status: string
  required_approvals: number
  current_approvals: number
  reason: string | null
  created_at: string
}

export interface ApprovalPolicy {
  id: number
  name: string
  organization_id: number | null
  transfer_type: string | null
  min_amount: number
  required_approvals: number
  require_separate_approver: boolean
  is_active: boolean
}

export interface CreatePolicyPayload {
  name: string
  organization_id?: number | null
  transfer_type?: string | null
  min_amount?: number
  required_approvals: number
  require_separate_approver?: boolean
}

export interface DecisionPayload {
  notes?: string
}

// ── Approvals queue ────────────────────────────────────────────────────────
export async function getApprovals(): Promise<Approval[]> {
  const { data } = await httpClient.get<Approval[]>("/approvals")
  return data
}

export async function approveRequest(
  id: number,
  payload?: DecisionPayload,
): Promise<Approval> {
  const { data } = await httpClient.post<Approval>(
    `/approvals/${id}/approve`,
    payload ?? {},
    idempotencyHeaders(`approve-${id}`),
  )
  return data
}

export async function rejectRequest(
  id: number,
  payload?: DecisionPayload,
): Promise<Approval> {
  const { data } = await httpClient.post<Approval>(
    `/approvals/${id}/reject`,
    payload ?? {},
    idempotencyHeaders(`reject-${id}`),
  )
  return data
}

// ── Policies ───────────────────────────────────────────────────────────────
export async function getPolicies(): Promise<ApprovalPolicy[]> {
  const { data } = await httpClient.get<ApprovalPolicy[]>("/approvals/policies")
  return data
}

export async function createPolicy(payload: CreatePolicyPayload): Promise<ApprovalPolicy> {
  const { data } = await httpClient.post<ApprovalPolicy>(
    "/approvals/policies",
    payload,
    idempotencyHeaders("create-policy"),
  )
  return data
}
