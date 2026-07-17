import { useEffect } from 'react';
import { useAuthStore } from '@portfolio/shared';
import AdminPage from './AdminPage';

function App() {
  const { initializeAuth, isAuthenticated, isAdmin, loading } = useAuthStore();

  // Инициализация авторизации
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  if (loading) return '';

  if (!isAuthenticated) window.location.href = '/login';
  if (!isAdmin()) window.location.href = '/portfolios';

  return <AdminPage />;
}

export default App;
