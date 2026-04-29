import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Budgets } from "../../views/DataPages"

export default function Route() {
  return <ProtectedRoute page="budgets"><Budgets /></ProtectedRoute>
}
