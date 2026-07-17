import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { authService } from '@portfolio/shared';
import { ROUTES } from 'src/constants/routes';
import { Alert, Button, Input, Spin, notification } from 'antd';

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { resetPassword } = authService();

  if (!token) {
    return (
      <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
        <div style={{width: '330px'}}>
          <Alert
            message="Недействительная ссылка"
            description="Ссылка для сброса пароля отсутствует или повреждена."
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <div style={{ textAlign: 'center' }}>
            <a href={ROUTES.LOGIN} style={{ textDecoration: 'none' }}>Вернуться ко входу</a>
          </div>
        </div>
      </main>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    notification.destroy();

    if (password !== confirmPassword) {
      notification.warning({ message: 'Пароли не совпадают', placement: 'topRight', duration: 5 });
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      notification.warning({ message: 'Пароль должен быть не менее 6 символов', placement: 'topRight', duration: 5 });
      setLoading(false);
      return;
    }

    const result = await resetPassword(token, password);

    if (result.success) {
      notification.success({ message: 'Пароль успешно сброшен. Теперь вы можете войти.', placement: 'topRight', duration: 5 });
      navigate(ROUTES.LOGIN);
    } else {
      notification.error({ message: result.error, placement: 'topRight', duration: 0 });
    }

    setLoading(false);
  };

  return (
    <main style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
      <form onSubmit={handleSubmit} style={{width: '330px'}}>
        <a href={ROUTES.HOME} style={{ display: 'flex', alignItems: 'center', marginBottom: 48, justifyContent: 'center', color: '#212529', textDecoration: 'none' }}>
          <img style={{ marginBottom: 0, marginRight: 8 }} src="/favicon.png" alt="" width="32" height="32" />
          <span style={{ fontSize: 'calc(1.275rem + .3vw)' }}>Portfolios</span>
        </a>

        <h1 style={{ fontSize: '1.75rem', fontWeight: 400, marginBottom: 16 }}>Новый пароль</h1>

        <div style={{ marginBottom: 8 }}>
          <Input.Password required placeholder="Новый пароль" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>

        <div style={{ marginBottom: 16 }}>
          <Input.Password required placeholder="Подтверждение пароля" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
        </div>

        <Button type="primary" htmlType="submit" disabled={loading} block style={{ marginBottom: 8 }}>
          {loading ? <Spin size="small" /> : 'Сбросить пароль'}
        </Button>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <a href={ROUTES.LOGIN} style={{ textDecoration: 'none' }}>Вернуться ко входу</a>
        </div>
      </form>
    </main>
  );
};

export default ResetPasswordPage;
