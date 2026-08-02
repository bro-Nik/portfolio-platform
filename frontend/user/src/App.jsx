import React, { useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { App as AntApp, ConfigProvider } from 'antd';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ChevronDown } from 'lucide-react';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/landing/LandingPage';
import AuthPage from './pages/auth/AuthPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import AppPage from './pages/app/AppPage';
import { ROUTES } from './constants/routes';
import { useAuthStore, useThemeStore } from '@portfolio/shared';
import useNavigationStore from './stores/navigationStore';
import { queryClient } from './queryClient';
import { TickerIdsProvider } from './hooks/TickerContext';
import { lightTheme, darkTheme } from './theme';

function App() {
  const { user, initializeAuth } = useAuthStore();
  const { theme } = useThemeStore();
  const prevUserId = useRef(user?.id);

  useEffect(() => {
    const userId = user?.id ?? null;
    if (prevUserId.current !== userId) {
      queryClient.clear();
      if (userId !== null) {
        const { userId: storedUserId } = useNavigationStore.getState();
        if (storedUserId !== userId) {
          useNavigationStore.setState({ userId });
          useNavigationStore.getState().actions.resetNavigation();
        }
      }
    }
    prevUserId.current = userId;
  }, [user?.id]);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const currentTheme = theme === 'dark' ? darkTheme : lightTheme;

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={currentTheme} modal={{ centered: true }} form={{ layout: 'vertical' }} table={{ size: 'small', pagination: false, showSorterTooltip: false }} select={{ suffixIcon: <ChevronDown size={14} /> }} renderEmpty={() => <div style={{ padding: '24px 0', color: 'var(--ant-color-text-tertiary)' }}>Нет данных</div>}>
        <AntApp style={{ height: '100%', display: 'contents' }}>
        <Router>
          <Routes>
            <Route path={ROUTES.HOME} element={<LandingPage />} />
            <Route path={ROUTES.LOGIN} element={<AuthPage type="login" />} />
            <Route path={ROUTES.REGISTER} element={<AuthPage type="register" />} />
            <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />
            <Route path={ROUTES.RESET_PASSWORD} element={<ResetPasswordPage />} />
            <Route path={ROUTES.APP} element={
                <ProtectedRoute>
                  <ThemeSetter />
                  <TickerIdsProvider>
                    <AppPage />
                  </TickerIdsProvider>
                </ProtectedRoute>
            } />

          </Routes>
        </Router>
        </AntApp>
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
