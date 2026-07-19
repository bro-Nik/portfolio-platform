import React, { useState, useEffect } from 'react';
import { Button, Card, Tag, Space, Modal, Typography, Avatar, Spin } from 'antd';
import { AlertTriangle, Monitor, Smartphone, Tablet, Globe, Trash2, LogOut, KeyRound, Mail, ShieldCheck, Smartphone as DeviceIcon } from 'lucide-react';
import { authService, useAuthStore } from '@portfolio/shared';
import { useNavigate } from 'react-router-dom';
import { useNavigation } from 'src/hooks/useNavigation';
import { useProfileQuery } from './useProfileQuery';
import { successToast, errorToast } from 'src/utils/notifications';
import ChangePasswordModal from './ChangePasswordModal';
import ChangeEmailModal from './ChangeEmailModal';
import DeleteAccountModal from './DeleteAccountModal';
import './SettingsPage.scss';

const { Text } = Typography;

const getInitials = (email) => {
  if (!email) return '?';
  return email.charAt(0).toUpperCase();
};

const getDeviceIcon = (deviceType) => {
  switch ((deviceType || '').toLowerCase()) {
    case 'mobile':
    case 'phone':
      return <Smartphone size={18} />;
    case 'tablet':
      return <Tablet size={18} />;
    default:
      return <Monitor size={18} />;
  }
};

const SettingsPage = () => {
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const navigate = useNavigate();
  const { user, logout: storeLogout } = useAuthStore();
  const { getSessions, deleteSession, logoutAll, resendVerification } = authService();
  const { activeSection } = useNavigation();
  const { data: profile, isLoading: profileLoading } = useProfileQuery({
    enabled: activeSection === 'settings',
  });

  const loadSessions = async () => {
    setSessionsLoading(true);
    const result = await getSessions();
    if (result.success) {
      setSessions(result.data || []);
    }
    setSessionsLoading(false);
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleResend = async () => {
    setResendLoading(true);
    const result = await resendVerification();
    setResendLoading(false);
    if (result.success) {
      successToast(result.message || 'Письмо отправлено');
    } else {
      errorToast(result.error || 'Ошибка отправки');
    }
  };

  const handleDeleteSession = (sessionId) => {
    Modal.confirm({
      title: 'Завершить сессию?',
      content: 'Вы будете разлогинены на этом устройстве.',
      okText: 'Завершить',
      cancelText: 'Отмена',
      okButtonProps: { danger: true },
      onOk: async () => {
        const result = await deleteSession(sessionId);
        if (result.success) {
          successToast('Сессия завершена');
          loadSessions();
        } else {
          errorToast(result.error || 'Ошибка удаления сессии');
        }
      },
    });
  };

  const handleLogoutAll = () => {
    Modal.confirm({
      title: 'Выйти со всех устройств?',
      content: 'Вы будете разлогинены везде, включая это устройство.',
      okText: 'Выйти',
      cancelText: 'Отмена',
      okButtonProps: { danger: true },
      onOk: async () => {
        const result = await logoutAll();
        if (result.success) {
          storeLogout();
          navigate('/login');
        } else {
          errorToast(result.error || 'Ошибка выхода');
        }
      },
    });
  };

  return (
    <div className="profile-page">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 600, color: 'var(--text-primary)' }}>Профиль</h1>
      </div>

      <Card style={{ marginBottom: 20 }} classNames={{ body: { padding: 24 } }}>
        <Spin spinning={profileLoading}>
          <div className="profile-header">
            <Avatar
              size={64}
              className="profile-avatar"
              style={{
                backgroundColor: '#6366f1',
                color: '#fff',
                fontSize: 24,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {getInitials(profile?.email || user?.email)}
            </Avatar>
            <div className="profile-info">
              <h2 className="profile-name">{user?.login || 'Пользователь'}</h2>
              <div className="profile-meta">
                <span className="profile-email">{profile?.email}</span>
                {profile && (
                  <span className={`verified-badge ${profile.isVerified ? 'verified' : 'unverified'}`}>
                    {profile.isVerified ? (
                      <><ShieldCheck size={12} /> Подтверждён</>
                    ) : (
                      <><AlertTriangle size={12} /> Не подтверждён</>
                    )}
                  </span>
                )}
              </div>
            </div>
          </div>
        </Spin>
      </Card>

      <Card style={{ marginBottom: 20 }} classNames={{ body: { padding: '8px 24px' } }}>
        <div className="security-item">
          <div className="security-item-left">
            <div className="security-item-icon">
              <Mail size={16} />
            </div>
            <div className="security-item-text">
              <div className="security-item-label">{profile?.email || '—'}</div>
              <div className="security-item-desc">Электронная почта</div>
            </div>
          </div>
          <Button type="primary" ghost size="small" onClick={() => setEmailModalOpen(true)}>
            Сменить
          </Button>
        </div>

        {profile && !profile.isVerified && (
          <div style={{
            display: 'flex',
            gap: 10,
            alignItems: 'flex-start',
            padding: '12px 0 12px 50px',
            borderTop: '1px solid var(--border-color)',
          }}>
            <AlertTriangle size={16} style={{ color: '#d48806', flexShrink: 0, marginTop: 2 }} />
            <div>
              <Text style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                Email не подтверждён. Подтверждение понадобится для восстановления доступа.
              </Text>
              <Button
                type="link"
                loading={resendLoading}
                onClick={handleResend}
                style={{ padding: 0, height: 'auto', fontSize: 13, marginLeft: 4 }}
              >
                Отправить повторно
              </Button>
            </div>
          </div>
        )}

        <div className="security-item">
          <div className="security-item-left">
            <div className="security-item-icon">
              <KeyRound size={16} />
            </div>
            <div className="security-item-text">
              <div className="security-item-label">Пароль</div>
              <div className="security-item-desc">Минимум 8 символов</div>
            </div>
          </div>
          <Button type="primary" ghost size="small" onClick={() => setPasswordModalOpen(true)}>
            Сменить
          </Button>
        </div>
      </Card>

      <Card classNames={{ body: { padding: '8px 24px' } }}>
        <div style={{ paddingTop: 8, paddingBottom: 4 }}>
          <div className="section-title">Активные сессии</div>
        </div>

        <Spin spinning={sessionsLoading}>
          {sessions.length === 0 && !sessionsLoading ? (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
              Нет активных сессий
            </div>
          ) : (
            <div className="sessions-list">
              {sessions.map((session) => (
                <div key={session.id} className="session-item">
                  <div className="session-icon">
                    {getDeviceIcon(session.deviceType)}
                  </div>
                  <div className="session-info">
                    <div className="session-tags">
                      {session.browser && <Tag>{session.browser}</Tag>}
                      {session.os && <Tag>{session.os}</Tag>}
                      {session.deviceType && <Tag>{session.deviceType}</Tag>}
                    </div>
                    <div className="session-details">
                      {session.ipAddress && <span>IP: {session.ipAddress}</span>}
                      {session.loginAt && (
                        <span>{session.ipAddress ? ' · ' : ''}Вход: {new Date(session.loginAt).toLocaleString('ru-RU')}</span>
                      )}
                      {session.lastActivityAt && (
                        <span> · Активность: {new Date(session.lastActivityAt).toLocaleString('ru-RU')}</span>
                      )}
                    </div>
                  </div>
                  <div className="session-action">
                    <Button
                      type="text"
                      danger
                      size="small"
                      icon={<Trash2 size={14} />}
                      onClick={() => handleDeleteSession(session.id)}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Spin>

        {sessions.length > 0 && (
          <div className="logout-all-btn" style={{ paddingBottom: 8 }}>
            <Button
              danger
              icon={<LogOut size={14} />}
              onClick={handleLogoutAll}
            >
              Выйти со всех устройств
            </Button>
          </div>
        )}
      </Card>

      <Card style={{ marginTop: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>
              Удаление аккаунта
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Безвозвратное удаление всех ваших данных
            </div>
          </div>
          <Button
            danger
            type="primary"
            icon={<Trash2 size={14} />}
            onClick={() => setDeleteModalOpen(true)}
          >
            Удалить аккаунт
          </Button>
        </div>
      </Card>

      <ChangePasswordModal open={passwordModalOpen} onClose={() => setPasswordModalOpen(false)} />
      <ChangeEmailModal open={emailModalOpen} onClose={() => setEmailModalOpen(false)} />
      <DeleteAccountModal open={deleteModalOpen} onClose={() => setDeleteModalOpen(false)} />
    </div>
  );
};

export default SettingsPage;
