import { ProtectedRoute } from "../../components/ProtectedRoute"
import { StatementsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="statements"><StatementsPage /></ProtectedRoute>
}
