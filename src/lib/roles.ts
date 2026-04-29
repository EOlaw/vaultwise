/**
 * Single source of truth for role-based page access.
 * Both AppLayout (sidebar filtering) and ProtectedRoute (guard) import from here.
 */

export type Role =
  | "admin"
  | "operator"
  | "owner"
  | "approver"
  | "viewer"
  | "user"

export type PageKey =
  | "dashboard"
  | "transactions"
  | "accounts"
  | "organizations"
  | "payees"
  | "transfers"
  | "approvals"
  | "risk"
  | "ledger"
  | "statements"
  | "cards"
  | "disputes"
  | "notifications"
  | "budgets"
  | "analytics"
  | "reports"
  | "securityCenter"
  | "settings"
  | "admin"

/** Pages each role may visit. The sidebar and the route guard both enforce this. */
export const ROLE_PAGES: Record<Role, ReadonlySet<PageKey>> = {
  admin: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "organizations", "payees",
    "transfers", "approvals", "risk", "ledger", "statements", "cards",
    "disputes", "notifications", "budgets", "analytics", "reports",
    "securityCenter", "settings", "admin",
  ]),

  operator: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "organizations", "payees",
    "transfers", "approvals", "statements", "cards", "disputes",
    "notifications", "budgets", "analytics", "reports", "securityCenter", "settings",
  ]),

  owner: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "organizations", "payees",
    "transfers", "approvals", "statements", "cards", "disputes",
    "notifications", "budgets", "analytics", "reports", "securityCenter", "settings",
  ]),

  approver: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "approvals",
    "notifications", "securityCenter", "settings",
  ]),

  viewer: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "notifications",
    "securityCenter", "settings",
  ]),

  /** Customer / end-user role */
  user: new Set<PageKey>([
    "dashboard", "transactions", "accounts", "cards",
    "statements", "reports", "notifications", "securityCenter", "settings",
  ]),
}

/** Returns true when the given role is allowed to access the page. */
export function canAccess(role: Role | string | undefined, page: PageKey): boolean {
  if (!role) return false
  const allowed = ROLE_PAGES[role as Role] ?? ROLE_PAGES.user
  return allowed.has(page)
}

/** The fallback redirect for a role that has no access to the requested page. */
export const ROLE_HOME: Record<Role, string> = {
  admin:    "/dashboard",
  operator: "/dashboard",
  owner:    "/dashboard",
  approver: "/approvals",
  viewer:   "/dashboard",
  user:     "/dashboard",
}
