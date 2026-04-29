import { ProtectedRoute } from "../../components/ProtectedRoute"
import { OrganizationsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="organizations"><OrganizationsPage /></ProtectedRoute>
}
