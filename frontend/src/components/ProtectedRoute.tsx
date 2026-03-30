import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuth((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/auth" replace />
}
