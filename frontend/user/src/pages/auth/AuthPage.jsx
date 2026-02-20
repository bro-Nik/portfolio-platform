import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { ROUTES } from '/app/src/constants/routes';
import { useToastStore } from '/app/src/stores/toastStore';
import { authService } from '/app/src/services/auth';
import { useAuthStore } from '/app/src/stores/authStore';

const AuthPage = ({ type }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { addToast, clearToasts } = useToastStore();
  const { login, register } = authService();
  const { isAuthenticated, loading: authLoading, login: authLogin } = useAuthStore();
  const isLogin = type === 'login';

  if (authLoading) return <div></div>;

  if (isAuthenticated) return <Navigate to={ROUTES.APP} replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    clearToasts();

    // Валидация для регистрации
    if (!isLogin && password !== confirmPassword) {
      addToast('Пароли не совпадают', 'warning');
      setLoading(false);
      return;
    }

    const handler = isLogin ? login : register;
    const result = await handler(email, password)
    
    if (result.success) {
      authLogin(result.data);
    } else {
      addToast(result.error, 'error');
    }
    
    setLoading(false);
  };

  const title = isLogin ? 'Вход' : 'Регистрация';
  const submitText = isLogin ? 'Вход' : 'Зарегистрироваться';
  const alternativeLink = isLogin ? ROUTES.REGISTER : ROUTES.LOGIN;
  const alternativeText = isLogin ? 'Регистрация' : 'Вход';

  return (
    <main className="m-auto">
      <form onSubmit={handleSubmit} style={{width: '330px'}}>
        <a href={ROUTES.HOME} className="d-flex align-items-center mb-5 justify-content-center link-body-emphasis text-decoration-none">
          <img className="mb-0 me-2" src="/favicon.png" alt="" width="32" height="32" />
          <span className="fs-4">Portfolios</span>
        </a>

        <div className="d-flex align-items-center gap-2 mb-3">
          <h1 className="h3 fw-normal">{title}</h1>
          <div className="ms-auto d-flex gap-3">
            <a className="text-decoration-none" href={alternativeLink}>{alternativeText}</a>
            <a className="text-decoration-none" href={ROUTES.DEMO}>Демо</a>
          </div>
        </div>

        <div className="mb-2">
          <input id="email" type="email" required placeholder="Email" className="form-control" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>

        <div className="mb-2">
          <input type="password" required placeholder="Пароль" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>

        {!isLogin && (
          <div className="mb-3">
            <input type="password" placeholder="Подтверждение пароля" required className="form-control" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          </div>
        )}

        <button type="submit" disabled={loading} className="w-100 btn btn-sm btn-primary" >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              {submitText}...
            </div>
          ) : (
            submitText
          )}
        </button>
      </form>
    </main>
  );
};

export default AuthPage;
