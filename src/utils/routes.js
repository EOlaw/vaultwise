export const routes = {
  "/dashboard": "dashboard",
  "/transactions": "transactions",
  "/accounts": "accounts",
  "/organizations": "organizations",
  "/payees": "payees",
  "/transfers": "transfers",
  "/approvals": "approvals",
  "/risk": "risk",
  "/ledger": "ledger",
  "/statements": "statements",
  "/cards": "cards",
  "/disputes": "disputes",
  "/notifications": "notifications",
  "/budgets": "budgets",
  "/analytics": "analytics",
  "/reports": "reports",
  "/settings": "settings",
  "/security-center": "securityCenter",
  "/admin": "admin"
}

export const publicRoutes = {
  "/": "home",
  "/product": "product",
  "/pricing": "pricing",
  "/security": "security",
  "/contact": "contact"
}

export const authPaths = new Set(["/login", "/register"])
export const publicPaths = new Set(Object.keys(publicRoutes))

export const pagePaths = Object.fromEntries(
  Object.entries(routes).map(([path, page]) => [page, path])
)

export function pageFromPath(pathname) {
  return routes[pathname] || "dashboard"
}

export function publicPageFromPath(pathname) {
  return publicRoutes[pathname] || "home"
}
