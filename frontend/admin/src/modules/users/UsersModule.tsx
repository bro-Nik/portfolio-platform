import React, { useState, useMemo } from 'react';
import { Badge, Button, Space, Tabs } from 'antd';
import { UserAddOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { UserTable } from './components/UserTable';
import { UserFilterPanel } from './components/UserFilterPanel';
import { UserStatsCards } from './components/UserStatsCards';
import { useUsers } from './hooks/useUsers';
import { useUserModals } from './hooks/useUserModals';
import { usePersistedState } from '@portfolio/shared';
import { UserFilters } from '../../types/user';
import { QueryError } from '../../components/QueryError';

export const UsersModule: React.FC = () => {
  const { data: users = [], isLoading, error } = useUsers();
  const { userFormModal } = useUserModals();

  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<UserFilters>({ status: 'all', role: 'all' });
  const [activeTab, setActiveTab] = usePersistedState('users_tab', 'all');

  const quickStats = useMemo(() => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    return {
      total: users.length,
      active: users.filter(u => u.status === 'active').length,
      online: users.filter(u => u.online === true).length,
      admins: users.filter(u => u.role === 'admin').length,
      newMonth: users.filter(u => new Date(u.createdAt) >= thirtyDaysAgo).length,
    };
  }, [users]);

  const filteredUsers = useMemo(() => {
    let filtered = [...users];

    if (activeTab === 'online') {
      filtered = filtered.filter(u => u.online === true);
    } else if (activeTab === 'recent') {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      filtered = filtered.filter(u => new Date(u.createdAt) >= thirtyDaysAgo);
    } else if (activeTab !== 'all') {
      filtered = filtered.filter(u => u.status === activeTab);
    }

    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(u => u.email.toLowerCase().includes(searchLower));
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(u => u.status === filters.status);
    }
    if (filters.role !== 'all') {
      filtered = filtered.filter(u => u.role === filters.role);
    }

    filtered.sort((a, b) =>
      dayjs(b.lastActiveAt).valueOf() - dayjs(a.lastActiveAt).valueOf()
    );

    return filtered;
  }, [users, searchText, filters, activeTab]);

  if (error) return <QueryError title='Ошибка загрузки пользователей' error={error} />;

  return (
    <div style={{ margin: '0 auto' }}>
      <UserStatsCards quickStats={quickStats} />

      <UserFilterPanel
        filters={filters}
        setFilters={setFilters}
        searchText={searchText}
        setSearchText={setSearchText}
      />

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        style={{ marginTop: '16px' }}
        tabBarExtraContent={
          <Space>
            <Button icon={<ReloadOutlined />} loading={isLoading}>Обновить</Button>
            <Button type="primary" icon={<UserAddOutlined />} onClick={() => userFormModal()}>Добавить пользователя</Button>
          </Space>
        }
        items={[
          { key: 'all', label: 'Все пользователи' },
          { key: 'online', label: <span>Онлайн <Badge count={quickStats.online} style={{ backgroundColor: '#52c41a' }} /></span> },
          { key: 'active', label: <span>Активные <Badge count={quickStats.active} style={{ backgroundColor: '#52c41a' }} /></span> },
          { key: 'block', label: 'Заблокированные' },
          { key: 'recent', label: 'Недавние' },
        ]}
      />

      <UserTable data={filteredUsers} loading={isLoading} />
    </div>
  );
};
