import { ProtectedRoute } from "../../components/ProtectedRoute"
import { CardsPage } from "../../views/BankingPages"

export default function Route() {
  return <ProtectedRoute page="cards"><CardsPage /></ProtectedRoute>
}
