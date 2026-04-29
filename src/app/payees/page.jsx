import { ProtectedRoute } from "../../components/ProtectedRoute"
import { PayeesPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="payees"><PayeesPage /></ProtectedRoute>
}
