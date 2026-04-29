"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../context/AuthContext"
import { AppLayout } from "../layouts/AppLayout"

export function ProtectedPage({ page, children, adminOnly = false }) {
  const { user, hydrated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!hydrated) return
    if (!user) router.replace("/login")
    else if (adminOnly && user.role !== "admin") router.replace("/dashboard")
  }, [adminOnly, hydrated, router, user])

  if (!hydrated) return <main className="p-6 text-sm text-slate-600">Loading workspace...</main>
  if (!user) return <main className="p-6 text-sm text-slate-600">Redirecting to login...</main>
  if (adminOnly && user.role !== "admin") return <main className="p-6 text-sm text-slate-600">Redirecting...</main>
  return <AppLayout page={page}>{children}</AppLayout>
}
