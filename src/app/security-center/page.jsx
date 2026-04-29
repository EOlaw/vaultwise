import { ProtectedRoute } from "../../components/ProtectedRoute"
import { SecurityCenterPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="securityCenter"><SecurityCenterPage /></ProtectedRoute>
}
