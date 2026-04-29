/**
 * ProtectedRoute — wraps every authenticated page.
 *
 * Guards:
 *  1. Unauthenticated users → /login
 *  2. Authenticated users whose role does NOT include this page → /dashboard
 *     (or the role's home page per ROLE_HOME)
 *
 * This is the only place role-based routing enforcement lives.
 * The sidebar only hides links — it does NOT prevent direct URL access.
 */

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"
import { AppLayout } from "../layouts/AppLayout"
import { canAccess, ROLE_HOME, type PageKey, type Role } from "../lib/roles"

interface ProtectedRouteProps {
  /** The logical page key — must match a PageKey in src/lib/roles.ts */
  page: PageKey
  children: React.ReactNode
}

export function ProtectedRoute({ page, children }: ProtectedRouteProps) {
  const { user, hydrated } = useAuth()
  const router = useRouter()

  const role = user?.role as Role | undefined
  const allowed = hydrated && !!user && canAccess(role, page)

  useEffect(() => {
    if (!hydrated) return

    if (!user) {
      router.replace("/login")
      return
    }

    if (!canAccess(role, page)) {
      const home = ROLE_HOME[role as Role] ?? "/dashboard"
      router.replace(home)
    }
  }, [hydrated, user, role, page, router])

  // ── Loading / redirect states ─────────────────────────────────────────
  if (!hydrated) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50">
        <p className="text-xs text-slate-400">Loading workspace…</p>
      </main>
    )
  }

  if (!user) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50">
        <p className="text-xs text-slate-400">Redirecting to sign in…</p>
      </main>
    )
  }

  if (!allowed) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50">
        <p className="text-xs text-slate-400">Redirecting…</p>
      </main>
    )
  }

  return <AppLayout page={page}>{children}</AppLayout>
}

/**
 * Convenience re-export so existing page files that still import
 * `ProtectedPage` continue to compile without changes.
 * @deprecated Import ProtectedRoute directly.
 */
export { ProtectedRoute as ProtectedPage }
