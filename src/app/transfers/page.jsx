import { ProtectedRoute } from "../../components/ProtectedRoute"
import { TransfersPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="transfers"><TransfersPage /></ProtectedRoute>
}
