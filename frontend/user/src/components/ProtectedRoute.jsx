import { Navigate } from 'react-router-dom';
import { useAuthStore } from '/app/src/stores/authStore';
import { ROUTES } from '../constants/routes';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuthStore();

  if (loading) return <LoadingSpinner />;

  return isAuthenticated ? children : <Navigate to={ROUTES.LOGIN} replace />;
};

export default ProtectedRoute;
