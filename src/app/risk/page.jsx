import { ProtectedRoute } from "../../components/ProtectedRoute"
import { RiskPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="risk"><RiskPage /></ProtectedRoute>
}
