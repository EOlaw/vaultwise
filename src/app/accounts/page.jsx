import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Accounts } from "../../views/DataPages"

export default function Route() {
  return <ProtectedRoute page="accounts"><Accounts /></ProtectedRoute>
}
