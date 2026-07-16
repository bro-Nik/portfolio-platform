import React from 'react';
import { Modal, Button, Card, Row, Col, Tag, Space, Avatar, Divider, Tabs, Descriptions, Timeline, Statistic } from 'antd';
import {
  CheckCircleOutlined,
  HistoryOutlined,
  EditOutlined,
  LockOutlined,
  UnlockOutlined,
  DeleteOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { getUserRoleTag, getUserAvatar, getUserStatusTag } from '../utils';
import { formatRelativeTime, formatTimeSum } from '../../../utils/date';
import { useModalStore } from '@portfolio/shared';
import { useUserActions } from '../hooks/useUserActions';
import { useUserModals } from '../hooks/useUserModals';
import { User } from '../../../types/user';

interface UserDetailsModalProps { user: User }

export const UserDetailsModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { user }: UserDetailsModalProps = modalProps;
  const { updateUserStatus, logoutAllDevices } = useUserActions();
  const { userFormModal, userDeleteConfirmModal } = useUserModals();

  if (!user) return null;

  const userTotalActivity = user.totalActiveTime && user.createdAt
    ? ((user.totalActiveTime / ((Date.now() - new Date(user.createdAt).getTime()) / 1000)) * 100).toFixed(2)
    : '0';

  return (
    <Modal
      title={
        <Space>
          <Avatar src={getUserAvatar(user)} />
          <span>{user.email.split('@')[0]}</span>
        </Space>
      }
      open={true}
      onCancel={closeModal}
      footer={null}
      width={800}
    >
      <Tabs defaultActiveKey="info">
        <Tabs.TabPane tab="Информация" key="info">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card size="small" title="Основная информация">
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
                  <Descriptions.Item label="Роль">{getUserRoleTag(user.role)}</Descriptions.Item>
                  <Descriptions.Item label="Статус">
                    {getUserStatusTag(user.status)}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="Статистика">
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Statistic
                      title="Время на сайте"
                      value={formatTimeSum(user.totalActiveTime ?? 0)}
                      prefix={<HistoryOutlined />}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="Активность"
                      value={userTotalActivity}
                      suffix="%"
                      prefix={<CheckCircleOutlined />}
                    />
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        </Tabs.TabPane>

        <Tabs.TabPane tab="Сессии входов" key="history">
          <Timeline>
            {user.loginSessions?.map((login) => (
              <Timeline.Item key={login.id} color="green">
                <Space vertical size={2}>
                  <div>
                    <strong>{dayjs(login.lastActivityAt).format('DD.MM.YYYY HH:mm:ss')}</strong>
                    <Tag color="default" style={{ marginLeft: '8px' }}>
                      {formatRelativeTime(login.lastActivityAt)}
                    </Tag>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {login.ipAddress} • {login.browser}/{login.os}
                  </div>
                </Space>
              </Timeline.Item>
            ))}
          </Timeline>
        </Tabs.TabPane>
      </Tabs>

      <Divider />
      <Space>
        <Button
          icon={<EditOutlined />}
          onClick={() => userFormModal(user)}
        >
          Редактировать
        </Button>
        <Button
          icon={user.status === 'active' ? <LockOutlined /> : <UnlockOutlined />}
          onClick={() => updateUserStatus(user.id, user.status === 'active' ? 'block' : 'active')}
        >
          {user.status === 'active' ? 'Заблокировать' : 'Активировать'}
        </Button>
        <Button
          icon={<LogoutOutlined />}
          onClick={() => logoutAllDevices(user.id)}
        >
          Выход со всех устройств
        </Button>
        <Button
          danger
          icon={<DeleteOutlined />}
          onClick={() => userDeleteConfirmModal(user)}
        >
          Удалить
        </Button>
      </Space>
    </Modal>
  );
};
