import React from 'react';
import { Button, Space, Avatar, Badge, Dropdown } from 'antd';
import Table from 'src/components/Table';
import { LockOutlined, UnlockOutlined, DeleteOutlined, EyeOutlined, EditOutlined, MoreOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import { getUserRoleTag, getUserAvatar, getUserStatusTag } from '../utils';
import { formatRelativeTime, formatTimeSum } from '../../../utils/date';
import { User } from '../../../types/user';
import { useUserModals } from '../hooks/useUserModals';
import { useUserActions } from '../hooks/useUserActions';

interface UserTableProps {
  data: User[];
  loading: boolean;
}

export const UserTable: React.FC<UserTableProps> = ({ data, loading }) => {
  const { userDetailsModal, userFormModal, userDeleteConfirmModal } = useUserModals();
  const { updateUserStatus } = useUserActions();

  const columns: ColumnsType<User> = [
    {
      title: 'Пользователь',
      dataIndex: 'email',
      key: 'user',
      fixed: 'left',
      width: 200,
      render: (_: string, record: User) => (
        <Space>
          <Avatar
            src={getUserAvatar(record)}
            size="large"
            style={{ border: record.status === 'active' ? '2px solid #52c41a' : 'none' }}
          />
          <div style={{ lineHeight: 1.2 }}>
            <div>
              <Button
                type="link"
                onClick={() => userDetailsModal(record)}
                style={{ padding: 0, height: 'auto' }}
              >
                <strong>{record.email.split('@')[0]}</strong>
              </Button>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-admin-secondary)' }}>{record.email}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      width: 140,
      render: (role: string) => getUserRoleTag(role),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status: string) => getUserStatusTag(status),
    },
    {
      title: 'Активность',
      dataIndex: 'lastActiveAt',
      key: 'lastActiveAt',
      width: 140,
      render: (date: string, record: User) => (
        <Space>
          <Badge status={record.online ? 'success' : 'default'} dot />
          {formatRelativeTime(date)}
        </Space>
      ),
    },
    {
      title: 'Время на сайте',
      dataIndex: 'totalActiveTime',
      key: 'totalActiveTime',
      width: 120,
      render: (seconds: number) => formatTimeSum(seconds),
    },
    {
      key: 'actions',
      fixed: 'right',
      width: 80,
      render: (_: unknown, record: User) => {
        const menuItems: MenuProps['items'] = [
          {
            key: 'view',
            label: 'Подробнее',
            icon: <EyeOutlined />,
            onClick: () => userDetailsModal(record),
          },
          {
            key: 'edit',
            label: 'Редактировать',
            icon: <EditOutlined />,
            onClick: () => userFormModal(record),
          },
          {
            key: 'status',
            label: record.status === 'active' ? 'Заблокировать' : 'Активировать',
            icon: record.status === 'active' ? <LockOutlined /> : <UnlockOutlined />,
            onClick: () =>
              updateUserStatus(record.id, record.status === 'active' ? 'block' : 'active'),
          },
          { type: 'divider' },
          {
            key: 'delete',
            label: 'Удалить',
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => userDeleteConfirmModal(record),
          },
        ];

        return (
          <Dropdown menu={{ items: menuItems }} placement="bottomRight" trigger={['click']}>
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        );
      },
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="id"
      loading={loading}
      pagination={{ pageSize: 20, showTotal: (total) => `Всего ${total} пользователей` }}
      scroll={{ x: 1200 }}
    />
  );
};
