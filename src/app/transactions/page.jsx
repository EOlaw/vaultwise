import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Transactions } from "../../views/DataPages"

export default function Route() {
  return <ProtectedRoute page="transactions"><Transactions /></ProtectedRoute>
}
