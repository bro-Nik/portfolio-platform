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
import { useAuthStore, useThemeStore } from '@portfolio/shared';
import { queryClient } from './queryClient';
import { TickerIdsProvider } from './hooks/TickerContext';
import { lightTheme, darkTheme } from './theme';

function App() {
  const { initializeAuth } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const currentTheme = theme === 'dark' ? darkTheme : lightTheme;

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider select={{ suffixIcon: <ChevronDown size={14} /> }}>
        <Router>
          <Routes>
            <Route path={ROUTES.HOME} element={<LandingPage />} />
            <Route path={ROUTES.LOGIN} element={<AuthPage type="login" />} />
            <Route path={ROUTES.REGISTER} element={<AuthPage type="register" />} />
            <Route path={ROUTES.APP} element={
              <ConfigProvider theme={currentTheme}>
                <ProtectedRoute>
                  <ThemeSetter />
                  <TickerIdsProvider>
                    <AppPage />
                  </TickerIdsProvider>
                </ProtectedRoute>
              </ConfigProvider>
            } />
          </Routes>
        </Router>
      </ConfigProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

function ThemeSetter() {
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    return () => document.documentElement.removeAttribute('data-theme');
  }, [theme]);

  return null;
}

export default App;
