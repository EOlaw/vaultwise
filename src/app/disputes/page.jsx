import { ProtectedRoute } from "../../components/ProtectedRoute"
import { DisputesPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="disputes"><DisputesPage /></ProtectedRoute>
}
