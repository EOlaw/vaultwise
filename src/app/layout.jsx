import { AuthProvider } from "../context/AuthContext"
import "./globals.css"

export const metadata = {
  title: "VaultWise — Enterprise Banking Platform",
  description: "VaultWise is an enterprise banking and treasury management platform for finance teams that demand control, compliance, and clarity."
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}
