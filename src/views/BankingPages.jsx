"use client"

import { useState } from "react"
import {
  Bell,
  BadgeDollarSign,
  Building2,
  Calculator,
  CreditCard,
  FileText,
  Filter,
  KeyRound,
  Landmark,
  Plus,
  ListChecks,
  LockKeyhole,
  Power,
  PowerOff,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Siren,
  UserPlus,
} from "lucide-react"
import { api, idempotencyHeaders } from "../api/client"
import { useAuth } from "../context/AuthContext"
import { useApi } from "../hooks/useApi"

const money = (value) => `$${Number(value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
function errText(error) {
  const detail = error?.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join(", ")
  if (detail && typeof detail === "object") return JSON.stringify(detail)
  return detail || error.message
}

function toInt(value) {
  return value === "" || value === undefined || value === null ? undefined : Number(value)
}

function toNullableInt(value) {
  return value === "" || value === undefined || value === null ? null : Number(value)
}

function withKey(prefix) {
  return { headers: idempotencyHeaders(prefix) }
}

function useMutation(...reloads) {
  const [status, setStatus] = useState("")
  async function run(task, success = "Saved") {
    setStatus("")
    try {
      await task()
      setStatus(success)
      reloads.forEach((reload) => reload?.())
    } catch (error) {
      setStatus(errText(error))
    }
  }
  return { status, run }
}

export function OrganizationsPage() {
  const orgs = useApi("/organizations", [])
  const accounts = useApi("/accounts", [])
  const users = useApi("/users", [])
  const [orgForm, setOrgForm] = useState({ name: "", legal_name: "", tax_id_last4: "", industry: "", city: "", state: "" })
  const [selectedOrg, setSelectedOrg] = useState("")
  const [memberForm, setMemberForm] = useState({ user_id: "", role: "viewer", title: "" })
  const [entitlementForm, setEntitlementForm] = useState({ account_id: "", user_id: "", can_view: true, can_transact: false, can_approve: false, daily_limit: "", monthly_limit: "" })
  const orgId = selectedOrg || orgs.data[0]?.id || ""
  const memberships = useApi(orgId ? `/organizations/${orgId}/memberships` : null, [])
  const entitlements = useApi(orgId ? `/organizations/${orgId}/entitlements` : null, [])
  const mutation = useMutation(orgs.reload, memberships.reload, entitlements.reload)

  return (
    <Page title="Business Banking" eyebrow="Organizations" icon={Building2} description="Companies, members, and account entitlements.">
      <div className="grid gap-3 xl:grid-cols-[1fr_0.85fr]">
        <DataTable title="Organizations" rows={orgs.data} columns={["name", "legal_name", "status", "industry", "city", "state"]} />
        <FormPanel title="Create Organization" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/organizations", { ...orgForm, country: "United States" }), "Organization created")}>
          <Field label="Name" value={orgForm.name} onChange={(name) => setOrgForm({ ...orgForm, name })} />
          <Field label="Legal name" value={orgForm.legal_name} onChange={(legal_name) => setOrgForm({ ...orgForm, legal_name })} />
          <div className="grid gap-2 sm:grid-cols-2">
            <Field label="Tax ID last4" value={orgForm.tax_id_last4} onChange={(tax_id_last4) => setOrgForm({ ...orgForm, tax_id_last4 })} />
            <Field label="Industry" value={orgForm.industry} onChange={(industry) => setOrgForm({ ...orgForm, industry })} />
            <Field label="City" value={orgForm.city} onChange={(city) => setOrgForm({ ...orgForm, city })} />
            <Field label="State" value={orgForm.state} onChange={(state) => setOrgForm({ ...orgForm, state })} />
          </div>
        </FormPanel>
      </div>

      <div className="grid gap-3 xl:grid-cols-2">
        <section className="space-y-3">
          <SelectField label="Selected organization" value={orgId} onChange={setSelectedOrg} options={orgs.data.map((org) => [org.id, org.name])} />
          <DataTable title="Members" rows={memberships.data} columns={["user_id", "role", "status", "title", "can_invite_members"]} />
          <DataTable title="Entitlements" rows={entitlements.data} columns={["account_id", "user_id", "can_view", "can_transact", "can_approve", "daily_limit", "monthly_limit", "status"]} />
        </section>
        <section className="space-y-3">
          <FormPanel title="Add Member" status={mutation.status} onSubmit={() => mutation.run(() => api.post(`/organizations/${orgId}/memberships`, { ...memberForm, user_id: toInt(memberForm.user_id) }), "Member added")}>
            <SelectField label="User" value={memberForm.user_id} onChange={(user_id) => setMemberForm({ ...memberForm, user_id })} options={users.data.map((user) => [user.id, `${user.full_name} (${user.email})`])} />
            <SelectField label="Role" value={memberForm.role} onChange={(role) => setMemberForm({ ...memberForm, role })} options={["owner", "admin", "operator", "approver", "viewer"].map((role) => [role, role])} />
            <Field label="Title" value={memberForm.title} onChange={(title) => setMemberForm({ ...memberForm, title })} />
          </FormPanel>
          <FormPanel title="Grant Entitlement" status={mutation.status} onSubmit={() => mutation.run(() => api.post(`/organizations/${orgId}/entitlements`, { ...entitlementForm, account_id: toInt(entitlementForm.account_id), user_id: toInt(entitlementForm.user_id), daily_limit: entitlementForm.daily_limit || null, monthly_limit: entitlementForm.monthly_limit || null }), "Entitlement saved")}>
            <SelectField label="Account" value={entitlementForm.account_id} onChange={(account_id) => setEntitlementForm({ ...entitlementForm, account_id })} options={accounts.data.map((account) => [account.id, `${account.name} #${account.id}`])} />
            <SelectField label="User" value={entitlementForm.user_id} onChange={(user_id) => setEntitlementForm({ ...entitlementForm, user_id })} options={users.data.map((user) => [user.id, user.email])} />
            <ToggleRow items={[
              ["View", entitlementForm.can_view, (can_view) => setEntitlementForm({ ...entitlementForm, can_view })],
              ["Transact", entitlementForm.can_transact, (can_transact) => setEntitlementForm({ ...entitlementForm, can_transact })],
              ["Approve", entitlementForm.can_approve, (can_approve) => setEntitlementForm({ ...entitlementForm, can_approve })],
            ]} />
            <div className="grid gap-2 sm:grid-cols-2">
              <Field label="Daily limit" value={entitlementForm.daily_limit} onChange={(daily_limit) => setEntitlementForm({ ...entitlementForm, daily_limit })} />
              <Field label="Monthly limit" value={entitlementForm.monthly_limit} onChange={(monthly_limit) => setEntitlementForm({ ...entitlementForm, monthly_limit })} />
            </div>
          </FormPanel>
        </section>
      </div>
    </Page>
  )
}

export function PayeesPage() {
  const payees = useApi("/beneficiaries", [])
  const orgs = useApi("/organizations", [])
  const accounts = useApi("/accounts", [])
  const [form, setForm] = useState({ organization_id: "", beneficiary_type: "external_ach", display_name: "", bank_name: "", routing_number_last4: "", account_number_last4: "", internal_account_id: "" })
  const mutation = useMutation(payees.reload)
  return (
    <Page title="Payees" eyebrow="Beneficiaries" icon={UserPlus} description="ACH, wire, bill-pay, and internal destinations.">
      <StepUpPanel />
      <div className="grid gap-3 xl:grid-cols-[1fr_0.8fr]">
        <DataTable title="Beneficiary Directory" rows={payees.data} columns={["display_name", "beneficiary_type", "status", "bank_name", "routing_number_last4", "account_number_last4", "organization_id"]} />
        <FormPanel title="Create Payee" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/beneficiaries", { ...form, organization_id: toNullableInt(form.organization_id), internal_account_id: toNullableInt(form.internal_account_id) }), "Payee created")}>
          <SelectField label="Organization" value={form.organization_id} onChange={(organization_id) => setForm({ ...form, organization_id })} options={orgs.data.map((org) => [org.id, org.name])} blank="Personal" />
          <SelectField label="Type" value={form.beneficiary_type} onChange={(beneficiary_type) => setForm({ ...form, beneficiary_type })} options={["external_ach", "wire", "bill_pay", "internal_account"].map((type) => [type, type])} />
          <Field label="Display name" value={form.display_name} onChange={(display_name) => setForm({ ...form, display_name })} />
          <Field label="Bank name" value={form.bank_name} onChange={(bank_name) => setForm({ ...form, bank_name })} />
          <div className="grid gap-2 sm:grid-cols-2">
            <Field label="Routing last4" value={form.routing_number_last4} onChange={(routing_number_last4) => setForm({ ...form, routing_number_last4 })} />
            <Field label="Account last4" value={form.account_number_last4} onChange={(account_number_last4) => setForm({ ...form, account_number_last4 })} />
          </div>
          <SelectField label="Internal account" value={form.internal_account_id} onChange={(internal_account_id) => setForm({ ...form, internal_account_id })} options={accounts.data.map((account) => [account.id, account.name])} blank="None" />
        </FormPanel>
      </div>
    </Page>
  )
}

export function TransfersPage() {
  const transfers = useApi("/transfers", [])
  const accounts = useApi("/accounts", [])
  const payees = useApi("/beneficiaries", [])
  const orgs = useApi("/organizations", [])
  const [form, setForm] = useState({ organization_id: "", from_account_id: "", to_account_id: "", beneficiary_id: "", transfer_type: "external_ach", amount: "", memo: "", scheduled_for: "" })
  const mutation = useMutation(transfers.reload)
  const payload = {
    organization_id: toNullableInt(form.organization_id),
    from_account_id: toInt(form.from_account_id),
    transfer_type: form.transfer_type,
    amount: form.amount,
    currency: "USD",
    memo: form.memo || null,
    scheduled_for: form.scheduled_for || null,
    ...(form.transfer_type === "internal" ? { to_account_id: toInt(form.to_account_id) } : { beneficiary_id: toInt(form.beneficiary_id) }),
  }
  return (
    <Page title="Transfers" eyebrow="Money movement" icon={Landmark} description="Draft, submit, approve, cancel, and post transfer instructions.">
      <StepUpPanel />
      <div className="grid gap-3 xl:grid-cols-[1.1fr_0.8fr]">
        <DataTable
          title="Transfer Queue"
          rows={transfers.data}
          columns={["id", "transfer_type", "status", "amount", "from_account_id", "to_account_id", "beneficiary_id", "memo", "scheduled_for"]}
          actions={(row) => (
            <div className="flex gap-1">
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/transfers/${row.id}/submit`, {}, withKey("submit-transfer")), "Submitted")}>Submit</button>
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/transfers/${row.id}/cancel`, {}, withKey("cancel-transfer")), "Cancelled")}>Cancel</button>
            </div>
          )}
        />
        <FormPanel title="Create Transfer" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/transfers", payload, withKey("create-transfer")), "Transfer created")}>
          <SelectField label="Organization" value={form.organization_id} onChange={(organization_id) => setForm({ ...form, organization_id })} options={orgs.data.map((org) => [org.id, org.name])} blank="Personal" />
          <SelectField label="From account" value={form.from_account_id} onChange={(from_account_id) => setForm({ ...form, from_account_id })} options={accounts.data.map((account) => [account.id, `${account.name} ${money(account.current_balance)}`])} />
          <SelectField label="Type" value={form.transfer_type} onChange={(transfer_type) => setForm({ ...form, transfer_type })} options={["internal", "external_ach", "wire", "bill_pay"].map((type) => [type, type])} />
          {form.transfer_type === "internal" ? (
            <SelectField label="To account" value={form.to_account_id} onChange={(to_account_id) => setForm({ ...form, to_account_id })} options={accounts.data.map((account) => [account.id, account.name])} />
          ) : (
            <SelectField label="Payee" value={form.beneficiary_id} onChange={(beneficiary_id) => setForm({ ...form, beneficiary_id })} options={payees.data.map((payee) => [payee.id, payee.display_name])} />
          )}
          <div className="grid gap-2 sm:grid-cols-2">
            <Field label="Amount" value={form.amount} onChange={(amount) => setForm({ ...form, amount })} />
            <Field label="Scheduled for" type="date" value={form.scheduled_for} onChange={(scheduled_for) => setForm({ ...form, scheduled_for })} />
          </div>
          <TextField label="Memo" value={form.memo} onChange={(memo) => setForm({ ...form, memo })} />
        </FormPanel>
      </div>
    </Page>
  )
}

export function ApprovalsPage() {
  const approvals = useApi("/approvals", [])
  const policies = useApi("/approvals/policies", [])
  const orgs = useApi("/organizations", [])
  const [policyForm, setPolicyForm] = useState({ organization_id: "", name: "", transfer_type: "", min_amount: "1000.00", required_approvals: "1", require_separate_approver: true })
  const [notes, setNotes] = useState("")
  const mutation = useMutation(approvals.reload, policies.reload)
  return (
    <Page title="Approvals" eyebrow="Dual control" icon={ListChecks} description="Approval requests and policy thresholds.">
      <StepUpPanel />
      <div className="grid gap-3 xl:grid-cols-[1.1fr_0.8fr]">
        <DataTable
          title="Approval Queue"
          rows={approvals.data}
          columns={["id", "transfer_id", "status", "required_approvals", "current_approvals", "reason", "created_at"]}
          actions={(row) => (
            <div className="flex gap-1">
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/approvals/${row.id}/approve`, { notes }, withKey("approve")), "Approved")}>Approve</button>
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/approvals/${row.id}/reject`, { notes }, withKey("reject")), "Rejected")}>Reject</button>
            </div>
          )}
        />
        <section className="space-y-3">
          <Field label="Decision notes" value={notes} onChange={setNotes} />
          <FormPanel title="Create Policy" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/approvals/policies", { ...policyForm, organization_id: toNullableInt(policyForm.organization_id), transfer_type: policyForm.transfer_type || null, required_approvals: Number(policyForm.required_approvals) }), "Policy created")}>
            <SelectField label="Organization" value={policyForm.organization_id} onChange={(organization_id) => setPolicyForm({ ...policyForm, organization_id })} options={orgs.data.map((org) => [org.id, org.name])} blank="Global" />
            <Field label="Name" value={policyForm.name} onChange={(name) => setPolicyForm({ ...policyForm, name })} />
            <div className="grid gap-2 sm:grid-cols-2">
              <Field label="Transfer type" value={policyForm.transfer_type} onChange={(transfer_type) => setPolicyForm({ ...policyForm, transfer_type })} />
              <Field label="Min amount" value={policyForm.min_amount} onChange={(min_amount) => setPolicyForm({ ...policyForm, min_amount })} />
            </div>
            <SelectField label="Required approvals" value={policyForm.required_approvals} onChange={(required_approvals) => setPolicyForm({ ...policyForm, required_approvals })} options={["1", "2", "3", "4"].map((n) => [n, n])} />
            <ToggleRow items={[["Separate approver", policyForm.require_separate_approver, (require_separate_approver) => setPolicyForm({ ...policyForm, require_separate_approver })]]} />
          </FormPanel>
        </section>
      </div>
      <DataTable title="Policies" rows={policies.data} columns={["name", "organization_id", "transfer_type", "min_amount", "required_approvals", "require_separate_approver", "is_active"]} />
    </Page>
  )
}

export function RiskPage() {
  const alerts = useApi("/risk/alerts", [])
  const cases = useApi("/compliance/cases", [])
  const [notes, setNotes] = useState("Reviewed by operations")
  const mutation = useMutation(alerts.reload, cases.reload)
  return (
    <Page title="Risk & Compliance" eyebrow="Controls" icon={ShieldAlert} description="Risk alerts, assignments, resolutions, and compliance case review.">
      <div className="grid gap-3 xl:grid-cols-[1.1fr_0.8fr]">
        <section className="space-y-3">
          <Field label="Resolution notes" value={notes} onChange={setNotes} />
          <DataTable
            title="Risk Alerts"
            rows={alerts.data}
            columns={["id", "severity", "status", "rule_code", "title", "transfer_id", "account_id", "created_at"]}
            actions={(row) => (
              <div className="flex gap-1">
                <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/risk/alerts/${row.id}/resolve`, { resolution_notes: notes }), "Resolved")}>Resolve</button>
                <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/risk/alerts/${row.id}/dismiss`, { resolution_notes: notes }), "Dismissed")}>Dismiss</button>
              </div>
            )}
          />
        </section>
        <DataTable title="Compliance Cases" rows={cases.data} columns={["case_number", "status", "alert_id", "assigned_to_user_id", "disposition", "created_at", "closed_at"]} />
      </div>
    </Page>
  )
}

export function LedgerPage() {
  const accounts = useApi("/accounts", [])
  const [selected, setSelected] = useState("")
  const accountId = selected || accounts.data[0]?.id || ""
  const balance = useApi(accountId ? `/ledger/accounts/${accountId}/balance` : null, null)
  const entries = useApi(accountId ? `/ledger/accounts/${accountId}/entries` : null, [])
  const holds = useApi(accountId ? `/ledger/holds?account_id=${accountId}` : "/ledger/holds", [])
  const mutation = useMutation(balance.reload, entries.reload, holds.reload)
  return (
    <Page title="Ledger" eyebrow="Posting" icon={Scale} description="Available balances, holds, entries, and snapshots.">
      <div className="grid gap-3 xl:grid-cols-[0.8fr_1.2fr]">
        <section className="space-y-3">
          <SelectField label="Account" value={accountId} onChange={setSelected} options={accounts.data.map((account) => [account.id, `${account.name} #${account.id}`])} />
          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
            <Metric label="Current balance" value={money(balance.data?.current_balance)} />
            <Metric label="Available balance" value={money(balance.data?.available_balance)} />
            <Metric label="Held amount" value={money(balance.data?.held_amount)} />
          </div>
          <button className="btn btn-primary w-full" onClick={() => mutation.run(() => api.post(`/ledger/accounts/${accountId}/snapshot`), "Snapshot created")}>Create Snapshot</button>
          {mutation.status && <StatusText value={mutation.status} />}
        </section>
        <section className="space-y-3">
          <DataTable title="Holds" rows={holds.data} columns={["id", "transfer_id", "card_authorization_id", "amount", "status", "reason", "expires_at", "released_at"]} />
          <DataTable title="Ledger Entries" rows={entries.data} columns={["effective_on", "direction", "event_type", "amount", "transfer_id", "transaction_id", "description"]} />
        </section>
      </div>
    </Page>
  )
}

export function StatementsPage() {
  const accounts = useApi("/accounts", [])
  const statements = useApi("/statements", [])
  const [form, setForm] = useState({ account_id: "", period_start: "2026-04-01", period_end: "2026-04-30" })
  const mutation = useMutation(statements.reload)
  return (
    <Page title="Statements" eyebrow="Documents" icon={FileText} description="Generated statement periods and line totals.">
      <div className="grid gap-3 xl:grid-cols-[1fr_0.75fr]">
        <DataTable title="Statement Runs" rows={statements.data} columns={["id", "account_id", "period_start", "period_end", "opening_balance", "closing_balance", "total_debits", "total_credits", "status"]} />
        <FormPanel title="Generate Statement" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/statements/generate", { ...form, account_id: toInt(form.account_id) }), "Statement generated")}>
          <SelectField label="Account" value={form.account_id} onChange={(account_id) => setForm({ ...form, account_id })} options={accounts.data.map((account) => [account.id, account.name])} />
          <Field label="Start" type="date" value={form.period_start} onChange={(period_start) => setForm({ ...form, period_start })} />
          <Field label="End" type="date" value={form.period_end} onChange={(period_end) => setForm({ ...form, period_end })} />
        </FormPanel>
      </div>
    </Page>
  )
}

export function CardsPage() {
  const cards = useApi("/cards", [])
  const accounts = useApi("/accounts", [])
  const authorizations = useApi("/cards/authorizations/list", [])
  const [selectedCardId, setSelectedCardId] = useState("")
  const [cardForm, setCardForm] = useState({ account_id: "", display_name: "", card_type: "debit", network: "visa", daily_limit: "500.00", monthly_limit: "2500.00" })
  const [controlForm, setControlForm] = useState({ allow_online: true, allow_card_present: true, allow_contactless: true, allow_international: false, allow_atm: true, require_pin: false, max_transaction_amount: "", blocked_merchant_categories: "" })
  const [authForm, setAuthForm] = useState({ card_id: "", amount: "", merchant_name: "", merchant_category: "", merchant_country: "US", card_not_present: true, channel: "online" })
  const mutation = useMutation(cards.reload, authorizations.reload)
  const selectedCard = cards.data.find((card) => String(card.id) === String(selectedCardId || authForm.card_id)) || cards.data[0]

  function selectCard(card) {
    setSelectedCardId(String(card.id))
    setAuthForm({ ...authForm, card_id: String(card.id) })
    setControlForm({
      allow_online: card.controls?.allow_online ?? true,
      allow_card_present: card.controls?.allow_card_present ?? true,
      allow_contactless: card.controls?.allow_contactless ?? true,
      allow_international: card.controls?.allow_international ?? false,
      allow_atm: card.controls?.allow_atm ?? true,
      require_pin: card.controls?.require_pin ?? false,
      max_transaction_amount: card.controls?.max_transaction_amount ?? "",
      blocked_merchant_categories: card.controls?.blocked_merchant_categories ?? "",
    })
  }

  return (
    <Page title="Cards" eyebrow="Enterprise issuing" icon={CreditCard} description="Issue credit, debit, savings-linked, and virtual cards with step-up security, tokenized records, and channel controls.">
      <StepUpPanel />
      <CardProductGrid />
      <div className="grid gap-3 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="space-y-3">
          <div className="grid gap-3 lg:grid-cols-2">
            {cards.data.map((card) => (
              <article key={card.id} className={`panel cursor-pointer p-3 hover:-translate-y-0.5 hover:shadow-[0_12px_28px_rgba(20,35,31,0.08)] ${selectedCard?.id === card.id ? "ring-2 ring-mint/20" : ""}`} onClick={() => selectCard(card)}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-[10px] font-black uppercase tracking-wide text-slate-500">{card.card_type} {card.network}</p>
                    <h2 className="mt-1 truncate text-sm font-black">{card.display_name}</h2>
                    <p className="mt-1 text-[11px] text-slate-500">**** {card.last4} · exp {card.expiry_month}/{card.expiry_year}</p>
                  </div>
                  <span className={`status-pill ${card.status === "active" ? "text-emerald-700" : "text-coral"}`}>{card.status}</span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
                  <div className="rounded-md bg-slate-50 px-2 py-1.5"><b>Daily</b><br />{money(card.daily_limit)}</div>
                  <div className="rounded-md bg-slate-50 px-2 py-1.5"><b>Monthly</b><br />{money(card.monthly_limit)}</div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  <button className="btn btn-secondary py-1" type="button" onClick={(event) => { event.stopPropagation(); mutation.run(() => api.post(`/cards/${card.id}/turn-off`), "Card turned off") }}><PowerOff size={13} /> Off</button>
                  <button className="btn btn-secondary py-1" type="button" onClick={(event) => { event.stopPropagation(); mutation.run(() => api.post(`/cards/${card.id}/turn-on`), "Card turned on") }}><Power size={13} /> On</button>
                  <button className="btn btn-secondary py-1" type="button" onClick={(event) => { event.stopPropagation(); mutation.run(() => api.post(`/cards/${card.id}/close`), "Card closed") }}>Close</button>
                </div>
              </article>
            ))}
          </div>
          <DataTable
            title="Issued Cards"
            rows={cards.data}
            columns={["display_name", "last4", "card_type", "network", "status", "account_id", "daily_limit", "monthly_limit"]}
          />
        </section>
        <FormPanel title="Issue Card" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/cards", { ...cardForm, account_id: toInt(cardForm.account_id), daily_limit: cardForm.daily_limit || null, monthly_limit: cardForm.monthly_limit || null }), "Card issued")}>
          <SelectField label="Account" value={cardForm.account_id} onChange={(account_id) => setCardForm({ ...cardForm, account_id })} options={accounts.data.map((account) => [account.id, account.name])} />
          <Field label="Display name" value={cardForm.display_name} onChange={(display_name) => setCardForm({ ...cardForm, display_name })} />
          <div className="grid gap-2 sm:grid-cols-2">
            <SelectField label="Type" value={cardForm.card_type} onChange={(card_type) => setCardForm({ ...cardForm, card_type })} options={["debit", "credit", "savings", "virtual"].map((type) => [type, type])} />
            <SelectField label="Network" value={cardForm.network} onChange={(network) => setCardForm({ ...cardForm, network })} options={["visa", "mastercard"].map((network) => [network, network])} />
            <Field label="Daily limit" value={cardForm.daily_limit} onChange={(daily_limit) => setCardForm({ ...cardForm, daily_limit })} />
            <Field label="Monthly limit" value={cardForm.monthly_limit} onChange={(monthly_limit) => setCardForm({ ...cardForm, monthly_limit })} />
          </div>
        </FormPanel>
      </div>
      <div className="grid gap-3 xl:grid-cols-[0.85fr_1fr]">
        <FormPanel title="Card Controls" status={mutation.status} onSubmit={() => mutation.run(() => api.patch(`/cards/${selectedCard?.id}/controls`, { ...controlForm, max_transaction_amount: controlForm.max_transaction_amount || null }), "Controls updated")}>
          <p className="small-copy">Selected: {selectedCard ? `${selectedCard.display_name} **** ${selectedCard.last4}` : "No card selected"}</p>
          <ToggleRow items={[
            ["Online", controlForm.allow_online, (allow_online) => setControlForm({ ...controlForm, allow_online })],
            ["In-store", controlForm.allow_card_present, (allow_card_present) => setControlForm({ ...controlForm, allow_card_present })],
            ["Tap to pay", controlForm.allow_contactless, (allow_contactless) => setControlForm({ ...controlForm, allow_contactless })],
            ["International", controlForm.allow_international, (allow_international) => setControlForm({ ...controlForm, allow_international })],
            ["ATM", controlForm.allow_atm, (allow_atm) => setControlForm({ ...controlForm, allow_atm })],
            ["Require PIN", controlForm.require_pin, (require_pin) => setControlForm({ ...controlForm, require_pin })],
          ]} />
          <Field label="Max transaction" value={controlForm.max_transaction_amount} onChange={(max_transaction_amount) => setControlForm({ ...controlForm, max_transaction_amount })} />
          <Field label="Blocked categories" value={controlForm.blocked_merchant_categories} onChange={(blocked_merchant_categories) => setControlForm({ ...controlForm, blocked_merchant_categories })} />
        </FormPanel>
        <DataTable
          title="Authorizations"
          rows={authorizations.data}
          columns={["id", "card_id", "merchant_name", "merchant_category", "channel", "amount", "status", "decline_reason", "transaction_id"]}
          actions={(row) => (
            <div className="flex gap-1">
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/cards/authorizations/${row.id}/capture`, {}, withKey("capture")), "Captured")}>Capture</button>
              <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/cards/authorizations/${row.id}/reverse`, {}, withKey("reverse")), "Reversed")}>Reverse</button>
            </div>
          )}
        />
      </div>
      <div className="grid gap-3 xl:grid-cols-[0.85fr_1fr]">
        <FormPanel title="Create Authorization" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/cards/authorizations", { ...authForm, card_id: toInt(authForm.card_id), amount: authForm.amount }, withKey("authorize-card")), "Authorization created")}>
          <SelectField label="Card" value={authForm.card_id} onChange={(card_id) => setAuthForm({ ...authForm, card_id })} options={cards.data.map((card) => [card.id, `${card.display_name} ${card.last4}`])} />
          <Field label="Amount" value={authForm.amount} onChange={(amount) => setAuthForm({ ...authForm, amount })} />
          <Field label="Merchant" value={authForm.merchant_name} onChange={(merchant_name) => setAuthForm({ ...authForm, merchant_name })} />
          <div className="grid gap-2 sm:grid-cols-2">
            <Field label="Category" value={authForm.merchant_category} onChange={(merchant_category) => setAuthForm({ ...authForm, merchant_category })} />
            <Field label="Country" value={authForm.merchant_country} onChange={(merchant_country) => setAuthForm({ ...authForm, merchant_country })} />
            <SelectField label="Channel" value={authForm.channel} onChange={(channel) => setAuthForm({ ...authForm, channel, card_not_present: channel === "online" })} options={["online", "card_present", "contactless", "atm"].map((channel) => [channel, channel])} />
          </div>
          <ToggleRow items={[["Card not present", authForm.card_not_present, (card_not_present) => setAuthForm({ ...authForm, card_not_present })]]} />
        </FormPanel>
      </div>
    </Page>
  )
}

function CardProductGrid() {
  const products = [
    ["Credit Card", "Credit line account, no ATM by default, online and in-store enabled.", BadgeDollarSign],
    ["Savings Card", "Savings-linked access with PIN-first and limited online exposure.", ShieldCheck],
    ["Debit Card", "Operating account card with ATM, online, in-store, and tap controls.", CreditCard],
    ["Virtual Card", "Online-only tokenized card for vendors and subscriptions.", LockKeyhole],
  ]
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {products.map(([title, text, Icon]) => (
        <article className="metric-card" key={title}>
          <Icon size={16} className="mb-2 text-mint" />
          <h2 className="section-title">{title}</h2>
          <p className="small-copy mt-1">{text}</p>
        </article>
      ))}
    </div>
  )
}

export function DisputesPage() {
  const disputes = useApi("/disputes", [])
  const transactions = useApi("/transactions", [])
  const authorizations = useApi("/cards/authorizations/list", [])
  const [form, setForm] = useState({ transaction_id: "", card_authorization_id: "", reason: "incorrect_amount", amount: "", description: "" })
  const [statusForm, setStatusForm] = useState({ status: "under_review", notes: "" })
  const mutation = useMutation(disputes.reload)
  return (
    <Page title="Disputes" eyebrow="Service cases" icon={Siren} description="Card and transaction disputes with staff lifecycle status.">
      <StepUpPanel />
      <div className="grid gap-3 xl:grid-cols-[1fr_0.85fr]">
        <DataTable
          title="Dispute Cases"
          rows={disputes.data}
          columns={["case_number", "reason", "status", "amount", "transaction_id", "card_authorization_id", "provisional_transaction_id", "opened_at"]}
          actions={(row) => (
            <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.patch(`/disputes/${row.id}/status`, statusForm, withKey("dispute-status")), "Status updated")}>Update</button>
          )}
        />
        <section className="space-y-3">
          <FormPanel title="Open Dispute" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/disputes", { ...form, transaction_id: toNullableInt(form.transaction_id), card_authorization_id: toNullableInt(form.card_authorization_id), amount: form.amount }), "Dispute opened")}>
            <SelectField label="Transaction" value={form.transaction_id} onChange={(transaction_id) => setForm({ ...form, transaction_id, card_authorization_id: "" })} options={transactions.data.map((tx) => [tx.id, `${tx.category} ${money(tx.amount)}`])} blank="None" />
            <SelectField label="Card authorization" value={form.card_authorization_id} onChange={(card_authorization_id) => setForm({ ...form, card_authorization_id, transaction_id: "" })} options={authorizations.data.map((auth) => [auth.id, `${auth.merchant_name} ${money(auth.amount)}`])} blank="None" />
            <SelectField label="Reason" value={form.reason} onChange={(reason) => setForm({ ...form, reason })} options={["fraud", "duplicate", "goods_not_received", "incorrect_amount", "cancelled_service", "other"].map((reason) => [reason, reason])} />
            <Field label="Amount" value={form.amount} onChange={(amount) => setForm({ ...form, amount })} />
            <TextField label="Description" value={form.description} onChange={(description) => setForm({ ...form, description })} />
          </FormPanel>
          <FormPanel title="Staff Status" status={mutation.status} onSubmit={() => Promise.resolve()}>
            <SelectField label="Status" value={statusForm.status} onChange={(status) => setStatusForm({ ...statusForm, status })} options={["open", "under_review", "provisional_credit", "won", "lost", "closed"].map((status) => [status, status])} />
            <TextField label="Notes" value={statusForm.notes} onChange={(notes) => setStatusForm({ ...statusForm, notes })} />
          </FormPanel>
        </section>
      </div>
    </Page>
  )
}

export function NotificationsPage() {
  const notifications = useApi("/notifications", [])
  const mutation = useMutation(notifications.reload)
  return (
    <Page title="Notifications" eyebrow="Inbox" icon={Bell} description="Transfer, statement, risk, and account activity notifications.">
      <div className="flex justify-end">
        <button className="btn btn-primary" onClick={() => mutation.run(() => api.post("/notifications/read-all"), "Marked read")}>Mark all read</button>
      </div>
      {mutation.status && <StatusText value={mutation.status} />}
      <DataTable
        title="Notification Feed"
        rows={notifications.data}
        columns={["priority", "notification_type", "title", "body", "read_at", "created_at"]}
        actions={(row) => <button className="btn btn-secondary py-1" onClick={() => mutation.run(() => api.post(`/notifications/${row.id}/read`), "Marked read")}>Read</button>}
      />
    </Page>
  )
}

export function AnalyticsPage() {
  const summary = useApi("/analytics/summary", {})
  const [loan, setLoan] = useState({ balance: "14500", annual_rate: "5.75", monthly_payment: "410" })
  const [investment, setInvestment] = useState({ principal: "10000", annual_rate: "7", years: "10", monthly_contribution: "250" })
  const [result, setResult] = useState({})
  const mutation = useMutation()
  return (
    <Page title="Analytics" eyebrow="Calculations" icon={Calculator} description="Cash flow, loan payoff, and investment projections.">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Object.entries(summary.data).map(([key, value]) => <Metric key={key} label={key.replaceAll("_", " ")} value={String(value)} />)}
      </div>
      <div className="grid gap-3 xl:grid-cols-2">
        <FormPanel title="Loan Payoff" status={mutation.status} onSubmit={() => mutation.run(async () => setResult({ loan: (await api.post("/analytics/loan-payoff", loan)).data }), "Calculated")}>
          <Field label="Balance" value={loan.balance} onChange={(balance) => setLoan({ ...loan, balance })} />
          <Field label="Annual rate" value={loan.annual_rate} onChange={(annual_rate) => setLoan({ ...loan, annual_rate })} />
          <Field label="Monthly payment" value={loan.monthly_payment} onChange={(monthly_payment) => setLoan({ ...loan, monthly_payment })} />
          {result.loan && <pre className="rounded-md bg-slate-50 p-3 text-xs">{JSON.stringify(result.loan, null, 2)}</pre>}
        </FormPanel>
        <FormPanel title="Investment Growth" status={mutation.status} onSubmit={() => mutation.run(async () => setResult({ investment: (await api.post("/analytics/investment-growth", { ...investment, years: Number(investment.years) })).data }), "Calculated")}>
          <Field label="Principal" value={investment.principal} onChange={(principal) => setInvestment({ ...investment, principal })} />
          <Field label="Annual rate" value={investment.annual_rate} onChange={(annual_rate) => setInvestment({ ...investment, annual_rate })} />
          <div className="grid gap-2 sm:grid-cols-2">
            <Field label="Years" value={investment.years} onChange={(years) => setInvestment({ ...investment, years })} />
            <Field label="Monthly contribution" value={investment.monthly_contribution} onChange={(monthly_contribution) => setInvestment({ ...investment, monthly_contribution })} />
          </div>
          {result.investment && <pre className="rounded-md bg-slate-50 p-3 text-xs">{JSON.stringify(result.investment, null, 2)}</pre>}
        </FormPanel>
      </div>
    </Page>
  )
}

export function SecurityCenterPage() {
  const auth = useAuth()
  const mfa = useApi("/auth/mfa", { enabled: false, devices: [] })
  const sessions = useApi("/auth/sessions", [])
  const [setup, setSetup] = useState(null)
  const [setupForm, setSetupForm] = useState({ label: "Authenticator app", code: "" })
  const mutation = useMutation(mfa.reload, sessions.reload)
  return (
    <Page title="Security Center" eyebrow="Identity" icon={LockKeyhole} description="MFA, step-up authorization, sessions, and trusted devices.">
      <div className="grid gap-3 xl:grid-cols-[0.85fr_1.15fr]">
        <section className="space-y-3">
          <StepUpPanel />
          <FormPanel title="MFA Setup" status={mutation.status} onSubmit={() => mutation.run(async () => setSetup((await api.post("/auth/mfa/setup", { label: setupForm.label })).data), "MFA setup created")}>
            <Field label="Device label" value={setupForm.label} onChange={(label) => setSetupForm({ ...setupForm, label })} />
            {setup && (
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs">
                <p className="font-semibold text-slate-600">Secret key</p>
                <p className="mt-1.5 break-all font-mono text-slate-800">{setup.secret}</p>
              </div>
            )}
          </FormPanel>
          {setup && (
            <FormPanel title="Confirm MFA" status={mutation.status} onSubmit={() => mutation.run(() => api.post(`/auth/mfa/${setup.device_id}/confirm`, { code: setupForm.code }), "MFA enabled")}>
              <Field label="Authenticator code" value={setupForm.code} onChange={(code) => setSetupForm({ ...setupForm, code })} />
            </FormPanel>
          )}
          <button className="btn btn-secondary w-full" onClick={() => mutation.run(() => auth.trustDevice(), "Device trusted")}>Trust current device</button>
        </section>
        <section className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric label="MFA status" value={mfa.data.enabled ? "Enabled" : "Disabled"} />
            <Metric label="Active sessions" value={String(sessions.data.filter((session) => session.is_active).length)} />
          </div>
          <DataTable title="MFA Devices" rows={mfa.data.devices || []} columns={["label", "device_type", "is_confirmed", "is_active", "last_used_at"]} />
          <DataTable title="Sessions" rows={sessions.data} columns={["device_label", "ip_address", "trusted_device", "step_up_expires_at", "is_active", "last_seen_at"]} />
        </section>
      </div>
    </Page>
  )
}

export function AdminOperationsPage() {
  const metrics = useApi("/admin/metrics", {})
  const users = useApi("/users", [])
  const audit = useApi("/admin/audit-logs", [])
  const security = useApi("/admin/security-events", [])
  const roles = useApi("/iam/roles", [])
  const permissions = useApi("/iam/permissions", [])
  const decisions = useApi("/iam/policy-decisions", [])
  const [roleForm, setRoleForm] = useState({ user_id: "", role_name: "" })
  const mutation = useMutation(users.reload)
  return (
    <Page title="Admin Panel" eyebrow="Governance" icon={ShieldCheck} description="Users, metrics, audit logs, and security events.">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {Object.entries(metrics.data).slice(0, 20).map(([key, value]) => <Metric key={key} label={key.replaceAll("_", " ")} value={String(value)} />)}
      </div>
      <div className="grid gap-3 xl:grid-cols-2">
        <DataTable title="Users" rows={users.data} columns={["id", "email", "full_name", "role", "is_active", "created_at"]} />
        <FormPanel title="Assign Role" status={mutation.status} onSubmit={() => mutation.run(() => api.post("/iam/assign-role", { ...roleForm, user_id: toInt(roleForm.user_id) }), "Role assigned")}>
          <SelectField label="User" value={roleForm.user_id} onChange={(user_id) => setRoleForm({ ...roleForm, user_id })} options={users.data.map((user) => [user.id, `${user.full_name} (${user.email})`])} />
          <SelectField label="Role" value={roleForm.role_name} onChange={(role_name) => setRoleForm({ ...roleForm, role_name })} options={roles.data.map((role) => [role.name, role.name])} />
        </FormPanel>
      </div>
      <div className="grid gap-3 xl:grid-cols-3">
        <DataTable title="IAM Roles" rows={roles.data} columns={["name", "description"]} />
        <DataTable title="Permissions" rows={permissions.data} columns={["code", "description"]} />
        <DataTable title="Policy Decisions" rows={decisions.data} columns={["permission", "decision", "user_id", "reason", "created_at"]} />
      </div>
      <DataTable title="Security Events" rows={security.data} columns={["event_type", "severity", "user_id", "ip_address", "created_at"]} />
      <DataTable title="Audit Logs" rows={audit.data} columns={["action", "actor_user_id", "resource_type", "resource_id", "outcome", "created_at"]} />
    </Page>
  )
}

function Page({ title, eyebrow, description, icon: Icon, children }) {
  return (
    <section className="customer-page">
      <header className="customer-header">
        <div className="customer-header-row">
          <div className="customer-title-block">
            <span className="customer-icon"><Icon size={17} /></span>
            <div className="min-w-0">
            <p className="eyebrow">{eyebrow}</p>
            <h1 className="page-title mt-1">{title}</h1>
              <p className="small-copy mt-1 max-w-3xl">{description}</p>
            </div>
          </div>
          <div className="quick-actions">
            <button className="quick-action" type="button"><Filter size={13} /> Filter</button>
            <button className="quick-action" type="button"><Plus size={13} /> New</button>
          </div>
        </div>
      </header>
      {children}
    </section>
  )
}

function StepUpPanel() {
  const auth = useAuth()
  const [form, setForm] = useState({ password: "", mfa_code: "" })
  const [status, setStatus] = useState("")
  return (
    <form
      className="panel grid gap-2 p-3 sm:grid-cols-[1fr_1fr_auto]"
      onSubmit={async (event) => {
        event.preventDefault()
        setStatus("")
        try {
          await auth.stepUp({ password: form.password || undefined, mfa_code: form.mfa_code || undefined })
          setStatus("Step-up active")
          setForm({ password: "", mfa_code: "" })
        } catch (error) {
          setStatus(errText(error))
        }
      }}
    >
      <Field label="Password" type="password" value={form.password} onChange={(password) => setForm({ ...form, password })} />
      <Field label="MFA code" value={form.mfa_code} onChange={(mfa_code) => setForm({ ...form, mfa_code })} />
      <div className="flex items-end">
        <button className="btn btn-primary w-full"><KeyRound size={14} /> Step up</button>
      </div>
      {status && <div className="sm:col-span-3"><StatusText value={status} /></div>}
    </form>
  )
}

function DataTable({ title, rows = [], columns = [], actions }) {
  return (
    <div className="table-panel">
      <div className="table-toolbar">
        <h2 className="section-title">{title}</h2>
        <span className="status-pill">{rows.length}</span>
      </div>
      <div className="overflow-auto">
        <table className="bank-table mt-0">
          <thead>
            <tr>
              {columns.map((column) => <th key={column}>{column.replaceAll("_", " ")}</th>)}
              {actions && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${title}-${row.id || row.case_number || row.session_key}`}>
                {columns.map((column) => <td key={column}>{formatCell(row, column)}</td>)}
                {actions && <td>{actions(row)}</td>}
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <td colSpan={columns.length + (actions ? 1 : 0)} className="text-center text-slate-500">No records.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function FormPanel({ title, status, onSubmit, children }) {
  return (
    <form
      className="form-panel"
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <h2 className="section-title">{title}</h2>
      {children}
      <button className="btn btn-primary w-full">Submit</button>
      {status && <StatusText value={status} />}
    </form>
  )
}

function Field({ label, value, onChange, type = "text" }) {
  return (
    <label className="field-label">
      <span className="field-caption">{label}</span>
      <input className="input" type={type} value={value ?? ""} onChange={(event) => onChange(event.target.value)} />
    </label>
  )
}

function TextField({ label, value, onChange }) {
  return (
    <label className="field-label">
      <span className="field-caption">{label}</span>
      <textarea className="textarea" value={value ?? ""} onChange={(event) => onChange(event.target.value)} />
    </label>
  )
}

function SelectField({ label, value, onChange, options, blank = "Select" }) {
  return (
    <label className="field-label">
      <span className="field-caption">{label}</span>
      <select className="select" value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
        <option value="">{blank}</option>
        {options.map(([optionValue, optionLabel]) => <option key={`${label}-${optionValue}`} value={optionValue}>{optionLabel}</option>)}
      </select>
    </label>
  )
}

function ToggleRow({ items }) {
  return (
    <div className="grid gap-2 sm:grid-cols-3">
      {items.map(([label, checked, onChange]) => (
        <label key={label} className="toggle-tile">
          <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
          {label}
        </label>
      ))}
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric-card">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1.5 truncate text-lg font-bold text-slate-900">{value}</p>
    </div>
  )
}

function StatusText({ value }) {
  const ok = !value.toLowerCase().includes("required") && !value.toLowerCase().includes("error") && !value.toLowerCase().includes("invalid") && !value.toLowerCase().includes("denied")
  return <p className={`rounded-md p-2 text-xs font-bold ${ok ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>{value}</p>
}

function formatCell(row, column) {
  const value = row[column]
  if (value === null || value === undefined || value === "") return <span className="text-slate-300">—</span>
  if (column.includes("amount") || column.includes("balance") || column.includes("limit") || column === "spent" || column === "remaining") return money(value)
  if (typeof value === "boolean") return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${value ? "bg-green-50 text-green-700" : "bg-slate-100 text-slate-500"}`}>
      {value ? "Yes" : "No"}
    </span>
  )
  if (column.includes("status") || column === "severity" || column === "priority") return <span className="status-pill">{String(value)}</span>
  if (typeof value === "object") return <span className="font-mono text-[11px] text-slate-500">{JSON.stringify(value)}</span>
  return <span className="text-slate-700">{String(value)}</span>
}
