import { ProtectedRoute } from "../../components/ProtectedRoute"
import { NotificationsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="notifications"><NotificationsPage /></ProtectedRoute>
}
