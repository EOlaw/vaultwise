import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Reports } from "../../views/DataPages"

export default function Route() {
  return <ProtectedRoute page="reports"><Reports /></ProtectedRoute>
}
