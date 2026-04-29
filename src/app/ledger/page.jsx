import { ProtectedRoute } from "../../components/ProtectedRoute"
import { LedgerPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="ledger"><LedgerPage /></ProtectedRoute>
}
