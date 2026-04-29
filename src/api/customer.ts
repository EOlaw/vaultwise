/**
 * Customer API — endpoints for the "user" role.
 * Covers: accounts (read), transactions (read), cards (view/freeze/unfreeze),
 *         statements (view + generate).
 *
 * This file must NEVER include operator/admin write mutations.
 */

import { httpClient, idempotencyHeaders } from "./client"

// ── Types ──────────────────────────────────────────────────────────────────
export interface Account {
  id: number
  name: string
  type: string
  institution: string
  opening_balance: number
  current_balance: number
  interest_rate: number | null
  status: string
}

export interface Transaction {
  id: number
  occurred_on: string
  type: "income" | "expense" | "transfer"
  category: string
  amount: number
  recurring_rule: string | null
  notes: string | null
}

export interface Card {
  id: number
  display_name: string
  last4: string
  card_type: "debit" | "credit" | "virtual"
  network: "visa" | "mastercard"
  status: "active" | "frozen" | "closed"
  account_id: number
  daily_limit: number | null
  monthly_limit: number | null
}

export interface Statement {
  id: number
  account_id: number
  period_start: string
  period_end: string
  opening_balance: number
  closing_balance: number
  total_debits: number
  total_credits: number
  status: string
}

export interface GenerateStatementPayload {
  account_id: number
  period_start: string
  period_end: string
}

// ── Accounts ───────────────────────────────────────────────────────────────
export async function getAccounts(): Promise<Account[]> {
  const { data } = await httpClient.get<Account[]>("/accounts")
  return data
}

export async function getAccount(id: number): Promise<Account> {
  const { data } = await httpClient.get<Account>(`/accounts/${id}`)
  return data
}

// ── Transactions ───────────────────────────────────────────────────────────
export async function getTransactions(): Promise<Transaction[]> {
  const { data } = await httpClient.get<Transaction[]>("/transactions")
  return data
}

// ── Cards ──────────────────────────────────────────────────────────────────
export async function getCards(): Promise<Card[]> {
  const { data } = await httpClient.get<Card[]>("/cards")
  return data
}

export async function freezeCard(cardId: number): Promise<Card> {
  const { data } = await httpClient.post<Card>(
    `/cards/${cardId}/freeze`,
    {},
    idempotencyHeaders(`freeze-${cardId}`),
  )
  return data
}

export async function unfreezeCard(cardId: number): Promise<Card> {
  const { data } = await httpClient.post<Card>(
    `/cards/${cardId}/unfreeze`,
    {},
    idempotencyHeaders(`unfreeze-${cardId}`),
  )
  return data
}

// ── Statements ─────────────────────────────────────────────────────────────
export async function getStatements(): Promise<Statement[]> {
  const { data } = await httpClient.get<Statement[]>("/statements")
  return data
}

export async function generateStatement(
  payload: GenerateStatementPayload,
): Promise<Statement> {
  const { data } = await httpClient.post<Statement>(
    "/statements/generate",
    payload,
    idempotencyHeaders("gen-statement"),
  )
  return data
}
