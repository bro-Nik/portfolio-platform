import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/landing/LandingPage';
import AuthPage from './pages/auth/AuthPage';
import AppPage from './pages/app/AppPage';
import { ROUTES } from './constants/routes';
import { useAuthStore } from '/app/src/stores/authStore';

function App() {
  const { initializeAuth } = useAuthStore();

  // Инициализация авторизации
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <Router>
      <Routes>
        <Route path={ROUTES.HOME} element={<LandingPage />} />
        <Route path={ROUTES.LOGIN} element={<AuthPage type={'login'} />} />
        <Route path={ROUTES.REGISTER} element={<AuthPage type={'register'} />} />
        <Route path={ROUTES.APP} element={<ProtectedRoute><AppPage /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;
