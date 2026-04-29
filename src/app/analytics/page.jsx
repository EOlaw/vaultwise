import { ProtectedRoute } from "../../components/ProtectedRoute"
import { AnalyticsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="analytics"><AnalyticsPage /></ProtectedRoute>
}
