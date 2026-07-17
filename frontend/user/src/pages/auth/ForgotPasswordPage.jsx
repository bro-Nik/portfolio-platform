import React, { useState } from 'react';
import { authService } from '@portfolio/shared';
import { ROUTES } from 'src/constants/routes';
import { Alert, Button, Input, Spin, notification } from 'antd';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const { forgotPassword } = authService();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    notification.destroy();

    const result = await forgotPassword(email);

    if (result.success) {
      setSent(true);
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

        <h1 style={{ fontSize: '1.75rem', fontWeight: 400, marginBottom: 16 }}>Восстановление доступа</h1>

        {sent ? (
          <Alert
            message="Проверьте вашу почту"
            description="Если email зарегистрирован, мы отправили ссылку для сброса пароля."
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
        ) : (
          <>
            <p style={{ color: '#6c757d', marginBottom: 16, fontSize: 14 }}>
              Введите email, указанный при регистрации. Мы отправим ссылку для сброса пароля.
            </p>

            <div style={{ marginBottom: 16 }}>
              <Input id="email" type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>

            <Button type="primary" htmlType="submit" disabled={loading} block style={{ marginBottom: 8 }}>
              {loading ? <Spin size="small" /> : 'Отправить ссылку'}
            </Button>
          </>
        )}

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <a href={ROUTES.LOGIN} style={{ textDecoration: 'none' }}>Вернуться ко входу</a>
        </div>
      </form>
    </main>
  );
};

export default ForgotPasswordPage;
