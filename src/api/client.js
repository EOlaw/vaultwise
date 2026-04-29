/**
 * Backward-compat shim — re-exports from the TypeScript client.
 * Views that still do `import { api, idempotencyHeaders } from "../api/client"`
 * will resolve here and get the typed implementation.
 *
 * Migrate call sites to import directly from "../api/client.ts" over time.
 */

export { httpClient, httpClient as api, idempotencyHeaders } from "./client.ts"
