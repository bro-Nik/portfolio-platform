import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ChevronDown } from 'lucide-react';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/landing/LandingPage';
import AuthPage from './pages/auth/AuthPage';
import AppPage from './pages/app/AppPage';
import { ROUTES } from './constants/routes';
import { useAuthStore } from '@portfolio/shared';
import { queryClient } from './queryClient';
import { TickerIdsProvider } from './hooks/queries/TickerContext';
import theme from './theme';

function App() {
  const { initializeAuth } = useAuthStore();

  // Инициализация авторизации
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={theme} select={{ suffixIcon: <ChevronDown size={14} /> }}>
        <Router>
          <Routes>
            <Route path={ROUTES.HOME} element={<LandingPage />} />
            <Route path={ROUTES.LOGIN} element={<AuthPage type={'login'} />} />
            <Route path={ROUTES.REGISTER} element={<AuthPage type={'register'} />} />
            <Route path={ROUTES.APP} element={<ProtectedRoute><TickerIdsProvider><AppPage /></TickerIdsProvider></ProtectedRoute>} />
          </Routes>
        </Router>
      </ConfigProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
