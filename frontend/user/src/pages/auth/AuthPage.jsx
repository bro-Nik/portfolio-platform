import React, { useEffect } from 'react';
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { authService, useAuthStore } from '@portfolio/shared';
import { ROUTES } from 'src/constants/routes';
import { Alert } from '@portfolio/shared';
import { Button, Input, Spin } from 'antd';
import { useNotifications } from '@portfolio/shared';
import { useAuthMutations } from 'src/hooks/useAuthMutations';

const AuthPage = ({ type }) => {
  const { destroy, warning, persistentError } = useNotifications();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [verifyStatus, setVerifyStatus] = React.useState(() =>
    searchParams.get('token') ? 'loading' : null,
  );

  const { getCurrentUser } = authService();
  const { isAuthenticated, loading: authLoading, login: authLogin } = useAuthStore();
  const { login, register, verifyEmail } = useAuthMutations();
  const isLogin = type === 'login';

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) return;

    verifyEmail.mutateAsync(token).then((result) => {
      setVerifyStatus(result.success ? 'success' : 'error');
      if (result.success) {
        getCurrentUser().then(u => u && authLogin(u));
      }
      navigate({ pathname: window.location.pathname }, { replace: true });
    });
  }, []);

  if (authLoading) return <div></div>;

  if (isAuthenticated) return <Navigate to={ROUTES.APP} replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setVerifyStatus(null);
    destroy();

    if (!isLogin && password !== confirmPassword) {
      warning('Пароли не совпадают');
      return;
    }

    const handler = isLogin ? login : register;
    const result = await handler.mutateAsync(isLogin ? { email, password } : { email, password });

    if (result.success) {
      authLogin(await getCurrentUser());
    } else {
      persistentError(result.error);
    }
  };

  const title = isLogin ? 'Вход' : 'Регистрация';
  const submitText = isLogin ? 'Вход' : 'Зарегистрироваться';
  const alternativeLink = isLogin ? ROUTES.REGISTER : ROUTES.LOGIN;
  const alternativeText = isLogin ? 'Регистрация' : 'Вход';

  return (
    <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
      <form onSubmit={handleSubmit} style={{width: '330px'}}>
        {verifyStatus === 'loading' && <Alert title="Подтверждение email..." type="info" style={{ marginBottom: 16 }} />}
        {verifyStatus === 'success' && <Alert title="Email успешно подтверждён" type="success" style={{ marginBottom: 16 }} />}
        {verifyStatus === 'error' && <Alert title="Ошибка подтверждения email" type="error" style={{ marginBottom: 16 }} />}

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
            <Input.Password placeholder="Подтверждение пароля" required value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          </div>
        )}

        {isLogin && (
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <a href={ROUTES.FORGOT_PASSWORD} style={{ fontSize: 13, textDecoration: 'none' }}>Забыли пароль?</a>
          </div>
        )}

        <Button type="primary" htmlType="submit" disabled={login.isPending || register.isPending} block style={{ marginBottom: 8 }}>
          {login.isPending || register.isPending ? <Spin size="small" /> : submitText}
        </Button>
      </form>
    </main>
  );
};

export default AuthPage;
