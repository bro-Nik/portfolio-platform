import { useEffect } from 'react';
import { App as AntApp } from 'antd';
import { useAuthStore } from '@portfolio/shared';
import AdminPage from './AdminPage';

function App() {
  const { initializeAuth, isAuthenticated, isAdmin, loading } = useAuthStore();

  // Инициализация авторизации
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Редирект по ролям
  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) {
      window.location.href = '/login';
    } else if (!isAdmin()) {
      window.location.href = '/portfolios';
    }
  }, [loading, isAuthenticated, isAdmin]);

  if (loading) return '';

  if (!isAuthenticated || !isAdmin()) return null;

  return <AntApp style={{ height: '100%', display: 'contents' }}><AdminPage /></AntApp>;
}

export default App;
