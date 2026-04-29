/**
 * Operator API — endpoints for "operator" and "owner" roles.
 * Covers: transfers, payees/beneficiaries, organizations, cards (full CRUD),
 *         card authorizations, disputes, budgets, analytics calculations.
 *
 * Requires step-up authentication for fund-movement mutations.
 */

import { httpClient, idempotencyHeaders } from "./client"
import type { Account, Card, Statement } from "./customer"

// ── Re-export customer read types for convenience ──────────────────────────
export type { Account, Card, Statement }

// ── Types ──────────────────────────────────────────────────────────────────
export interface Organization {
  id: number
  name: string
  legal_name: string
  tax_id_last4: string
  industry: string
  city: string
  state: string
  country: string
  status: string
}

export interface CreateOrgPayload {
  name: string
  legal_name: string
  tax_id_last4: string
  industry: string
  city: string
  state: string
  country?: string
}

export interface OrgMembership {
  id: number
  user_id: number
  role: string
  title: string
  status: string
  can_invite_members: boolean
}

export interface AddMemberPayload {
  user_id: number
  role: string
  title?: string
}

export interface Entitlement {
  id: number
  account_id: number
  user_id: number
  can_view: boolean
  can_transact: boolean
  can_approve: boolean
  daily_limit: number | null
  monthly_limit: number | null
  status: string
}

export interface GrantEntitlementPayload {
  account_id: number
  user_id: number
  can_view: boolean
  can_transact: boolean
  can_approve: boolean
  daily_limit?: number | null
  monthly_limit?: number | null
}

export interface Beneficiary {
  id: number
  display_name: string
  beneficiary_type: string
  status: string
  bank_name: string
  routing_number_last4: string
  account_number_last4: string
  organization_id: number | null
}

export interface CreateBeneficiaryPayload {
  display_name: string
  beneficiary_type: string
  bank_name?: string
  routing_number_last4?: string
  account_number_last4?: string
  organization_id?: number | null
  internal_account_id?: number | null
}

export interface Transfer {
  id: number
  transfer_type: string
  status: string
  amount: number
  currency: string
  from_account_id: number
  to_account_id: number | null
  beneficiary_id: number | null
  memo: string | null
  scheduled_for: string | null
}

export interface CreateTransferPayload {
  from_account_id: number
  transfer_type: string
  amount: number
  currency?: string
  memo?: string | null
  scheduled_for?: string | null
  organization_id?: number | null
  to_account_id?: number
  beneficiary_id?: number
}

export interface Dispute {
  id: number
  case_number: string
  reason: string
  status: string
  amount: number
  transaction_id: number | null
  card_authorization_id: number | null
  provisional_transaction_id: number | null
  opened_at: string
}

export interface OpenDisputePayload {
  transaction_id?: number | null
  card_authorization_id?: number | null
  reason: string
  amount: number
  description?: string
}

export interface CardAuthorization {
  id: number
  card_id: number
  merchant_name: string
  merchant_category: string
  amount: number
  status: string
  decline_reason: string | null
  transaction_id: number | null
}

export interface CreateCardPayload {
  account_id: number
  display_name: string
  card_type: "debit" | "credit" | "virtual"
  network: "visa" | "mastercard"
  daily_limit?: number | null
  monthly_limit?: number | null
}

export interface Budget {
  id: number
  month: string
  category: string
  limit_amount: number
  spent: number
  remaining: number
  progress: number
  overspent: boolean
}

export interface LoanPayoffPayload {
  balance: string
  annual_rate: string
  monthly_payment: string
}

export interface InvestmentGrowthPayload {
  principal: string
  annual_rate: string
  years: number
  monthly_contribution: string
}

// ── Organizations ──────────────────────────────────────────────────────────
export async function getOrganizations(): Promise<Organization[]> {
  const { data } = await httpClient.get<Organization[]>("/organizations")
  return data
}

export async function createOrganization(payload: CreateOrgPayload): Promise<Organization> {
  const { data } = await httpClient.post<Organization>("/organizations", {
    ...payload,
    country: payload.country ?? "United States",
  })
  return data
}

export async function getOrgMemberships(orgId: number): Promise<OrgMembership[]> {
  const { data } = await httpClient.get<OrgMembership[]>(`/organizations/${orgId}/memberships`)
  return data
}

export async function addOrgMember(orgId: number, payload: AddMemberPayload): Promise<OrgMembership> {
  const { data } = await httpClient.post<OrgMembership>(
    `/organizations/${orgId}/memberships`,
    payload,
    idempotencyHeaders("add-member"),
  )
  return data
}

export async function getOrgEntitlements(orgId: number): Promise<Entitlement[]> {
  const { data } = await httpClient.get<Entitlement[]>(`/organizations/${orgId}/entitlements`)
  return data
}

export async function grantEntitlement(orgId: number, payload: GrantEntitlementPayload): Promise<Entitlement> {
  const { data } = await httpClient.post<Entitlement>(
    `/organizations/${orgId}/entitlements`,
    payload,
    idempotencyHeaders("grant-entitlement"),
  )
  return data
}

// ── Beneficiaries / Payees ─────────────────────────────────────────────────
export async function getBeneficiaries(): Promise<Beneficiary[]> {
  const { data } = await httpClient.get<Beneficiary[]>("/beneficiaries")
  return data
}

export async function createBeneficiary(payload: CreateBeneficiaryPayload): Promise<Beneficiary> {
  const { data } = await httpClient.post<Beneficiary>(
    "/beneficiaries",
    payload,
    idempotencyHeaders("create-payee"),
  )
  return data
}

// ── Transfers ──────────────────────────────────────────────────────────────
export async function getTransfers(): Promise<Transfer[]> {
  const { data } = await httpClient.get<Transfer[]>("/transfers")
  return data
}

export async function createTransfer(payload: CreateTransferPayload): Promise<Transfer> {
  const { data } = await httpClient.post<Transfer>(
    "/transfers",
    payload,
    idempotencyHeaders("create-transfer"),
  )
  return data
}

export async function submitTransfer(id: number): Promise<Transfer> {
  const { data } = await httpClient.post<Transfer>(
    `/transfers/${id}/submit`,
    {},
    idempotencyHeaders(`submit-${id}`),
  )
  return data
}

export async function cancelTransfer(id: number): Promise<Transfer> {
  const { data } = await httpClient.post<Transfer>(
    `/transfers/${id}/cancel`,
    {},
    idempotencyHeaders(`cancel-${id}`),
  )
  return data
}

// ── Cards (operator-level) ─────────────────────────────────────────────────
export async function createCard(payload: CreateCardPayload): Promise<Card> {
  const { data } = await httpClient.post<Card>(
    "/cards",
    payload,
    idempotencyHeaders("issue-card"),
  )
  return data
}

export async function getCardAuthorizations(): Promise<CardAuthorization[]> {
  const { data } = await httpClient.get<CardAuthorization[]>("/cards/authorizations/list")
  return data
}

export async function createCardAuthorization(payload: {
  card_id: number
  amount: number
  merchant_name: string
  merchant_category: string
  merchant_country?: string
  card_not_present?: boolean
}): Promise<CardAuthorization> {
  const { data } = await httpClient.post<CardAuthorization>(
    "/cards/authorizations",
    payload,
    idempotencyHeaders("authorize-card"),
  )
  return data
}

export async function captureAuthorization(id: number): Promise<CardAuthorization> {
  const { data } = await httpClient.post<CardAuthorization>(
    `/cards/authorizations/${id}/capture`,
    {},
    idempotencyHeaders(`capture-${id}`),
  )
  return data
}

export async function reverseAuthorization(id: number): Promise<CardAuthorization> {
  const { data } = await httpClient.post<CardAuthorization>(
    `/cards/authorizations/${id}/reverse`,
    {},
    idempotencyHeaders(`reverse-${id}`),
  )
  return data
}

// ── Disputes ───────────────────────────────────────────────────────────────
export async function getDisputes(): Promise<Dispute[]> {
  const { data } = await httpClient.get<Dispute[]>("/disputes")
  return data
}

export async function openDispute(payload: OpenDisputePayload): Promise<Dispute> {
  const { data } = await httpClient.post<Dispute>(
    "/disputes",
    payload,
    idempotencyHeaders("open-dispute"),
  )
  return data
}

export async function updateDisputeStatus(
  id: number,
  status: string,
  notes?: string,
): Promise<Dispute> {
  const { data } = await httpClient.patch<Dispute>(
    `/disputes/${id}/status`,
    { status, notes },
    idempotencyHeaders(`dispute-status-${id}`),
  )
  return data
}

// ── Budgets ────────────────────────────────────────────────────────────────
export async function getBudgets(): Promise<Budget[]> {
  const { data } = await httpClient.get<Budget[]>("/budgets")
  return data
}

// ── Analytics calculations ─────────────────────────────────────────────────
export async function calculateLoanPayoff(payload: LoanPayoffPayload): Promise<Record<string, unknown>> {
  const { data } = await httpClient.post("/analytics/loan-payoff", payload)
  return data
}

export async function calculateInvestmentGrowth(payload: InvestmentGrowthPayload): Promise<Record<string, unknown>> {
  const { data } = await httpClient.post("/analytics/investment-growth", payload)
  return data
}
