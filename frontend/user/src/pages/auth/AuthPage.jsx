import React, { useEffect, useState } from 'react';
import { Navigate, useSearchParams, useNavigate } from 'react-router-dom';
import { authService, useAuthStore } from '@portfolio/shared';
import { ROUTES } from 'src/constants/routes';
import { Alert, Button, Input, Spin, notification } from 'antd';

const AuthPage = ({ type }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifyStatus, setVerifyStatus] = useState(null);

  const { login, register, verifyEmail, getCurrentUser } = authService();
  const { isAuthenticated, loading: authLoading, login: authLogin } = useAuthStore();
  const isLogin = type === 'login';

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) return;

    setVerifyStatus('loading');
    verifyEmail(token).then((result) => {
      setVerifyStatus(result.success ? 'success' : 'error');
      navigate({ pathname: window.location.pathname }, { replace: true });
    });
  }, []);

  if (authLoading) return <div></div>;

  if (isAuthenticated) return <Navigate to={ROUTES.APP} replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setVerifyStatus(null);
    setLoading(true);
    notification.destroy();

    // Валидация для регистрации
    if (!isLogin && password !== confirmPassword) {
      notification.warning({ message: 'Пароли не совпадают', placement: 'topRight', duration: 5 });
      setLoading(false);
      return;
    }

    const handler = isLogin ? login : register;
    const result = await handler(email, password)
    
    if (result.success) {
      authLogin(await getCurrentUser());
    } else {
      notification.error({ message: result.error, placement: 'topRight', duration: 0 });
    }
    
    setLoading(false);
  };

  const title = isLogin ? 'Вход' : 'Регистрация';
  const submitText = isLogin ? 'Вход' : 'Зарегистрироваться';
  const alternativeLink = isLogin ? ROUTES.REGISTER : ROUTES.LOGIN;
  const alternativeText = isLogin ? 'Регистрация' : 'Вход';

  return (
    <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
      <form onSubmit={handleSubmit} style={{width: '330px'}}>
        {verifyStatus === 'loading' && <Alert message="Подтверждение email..." type="info" showIcon style={{ marginBottom: 16 }} />}
        {verifyStatus === 'success' && <Alert message="Email успешно подтверждён" type="success" showIcon style={{ marginBottom: 16 }} />}
        {verifyStatus === 'error' && <Alert message="Ошибка подтверждения email" type="error" showIcon style={{ marginBottom: 16 }} />}

        <a href={ROUTES.HOME} style={{ display: 'flex', alignItems: 'center', marginBottom: 48, justifyContent: 'center', color: '#212529', textDecoration: 'none' }}>
          <img style={{ marginBottom: 0, marginRight: 8 }} src="/favicon.png" alt="" width="32" height="32" />
          <span style={{ fontSize: 'calc(1.275rem + .3vw)' }}>Portfolios</span>
        </a>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>{title}</h1>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 12 }}>
            <a style={{ textDecoration: 'none' }} href={alternativeLink}>{alternativeText}</a>
          </div>
        </div>

        <div style={{ marginBottom: 8 }}>
          <Input id="email" type="email" required placeholder="Email" value={email} onChange={(e) => { setVerifyStatus(null); setEmail(e.target.value); }} />
        </div>

        <div style={{ marginBottom: 8 }}>
          <Input.Password required placeholder="Пароль" value={password} onChange={(e) => { setVerifyStatus(null); setPassword(e.target.value); }} />
        </div>

        {!isLogin && (
          <div style={{ marginBottom: 16 }}>
            <Input.Password placeholder="Подтверждение пароля" required value={confirmPassword} onChange={(e) => { setVerifyStatus(null); setConfirmPassword(e.target.value); }} />
          </div>
        )}

        <Button type="primary" htmlType="submit" disabled={loading} block style={{ marginBottom: 8 }}>
          {loading ? <Spin size="small" /> : submitText}
        </Button>
      </form>
    </main>
  );
};

export default AuthPage;
