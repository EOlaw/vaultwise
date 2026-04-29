import { ProtectedRoute } from "../../components/ProtectedRoute"
import { Settings } from "../../views/DataPages"

export default function Route() {
  return <ProtectedRoute page="settings"><Settings /></ProtectedRoute>
}
