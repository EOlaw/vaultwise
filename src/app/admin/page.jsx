import { ProtectedRoute } from "../../components/ProtectedRoute"
import { AdminOperationsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="admin"><AdminOperationsPage /></ProtectedRoute>
}
