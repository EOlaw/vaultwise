import { ProtectedRoute } from "../../components/ProtectedRoute"
import { ApprovalsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="approvals"><ApprovalsPage /></ProtectedRoute>
}
