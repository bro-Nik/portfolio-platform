import { useEffect } from 'react';
import { useAuthStore } from '@shared';
import AdminPage from '/app/src/AdminPage';

function App() {
  const { initializeAuth, isAuthenticated, loading } = useAuthStore();

  // Инициализация авторизации
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  if (loading) return '';

  if (!isAuthenticated) window.location.href = '/login';

  return <AdminPage />;
}

export default App;
