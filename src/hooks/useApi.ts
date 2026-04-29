/**
 * Generic data-fetching hook backed by the shared HTTP client.
 * Uses the authenticated httpClient so the Authorization header is always sent.
 */

"use client"

import { useCallback, useEffect, useState } from "react"
import { httpClient } from "../api/client"

export interface UseApiResult<T> {
  data: T
  loading: boolean
  error: string
  reload: () => void
  setData: (next: T) => void
}

/**
 * Fetches `path` on mount and whenever `path` changes.
 * Pass `null` as `path` to skip the request (returns `fallback` immediately).
 *
 * @param path    API path relative to the base URL, e.g. "/accounts"
 * @param fallback Value used before the first successful response
 */
export function useApi<T>(path: string | null, fallback: T): UseApiResult<T> {
  const [data, setData] = useState<T>(fallback)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>("")

  const reload = useCallback((): (() => void) => {
    let mounted = true

    if (!path) {
      setData(fallback)
      setLoading(false)
      setError("")
      return () => { mounted = false }
    }

    setLoading(true)
    setError("")

    httpClient
      .get<T>(path)
      .then(({ data: response }) => {
        if (mounted) setData(response)
      })
      .catch((err: unknown) => {
        if (!mounted) return
        const message =
          (err as { response?: { data?: { detail?: string } }; message?: string })
            ?.response?.data?.detail ??
          (err as { message?: string })?.message ??
          "An unexpected error occurred."
        setError(message)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })

    return () => { mounted = false }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path])

  useEffect(() => {
    const cleanup = reload()
    return cleanup
  }, [reload])

  return { data, loading, error, reload, setData }
}
