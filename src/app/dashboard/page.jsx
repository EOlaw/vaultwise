import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Dashboard } from "../../views/Dashboard"

export default function Route() {
  return <ProtectedRoute page="dashboard"><Dashboard /></ProtectedRoute>
}
