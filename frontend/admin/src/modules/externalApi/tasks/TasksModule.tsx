import React, { useState, useMemo } from 'react';
import { Badge, Button, Space, Tabs } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { TaskTable } from './components/TaskTable';
import { TaskFilterPanel, TaskFilters } from './components/TaskFilterPanel';
import { TaskStatsCards } from './components/TaskStatsCards';
import { useTasks } from './hooks/useTasks';
import { useTaskModals } from './hooks/useTaskModals';
import { QueryError } from '../../../components/QueryError';

export const TasksModule: React.FC = () => {
  const { data: tasks = [], isLoading, error } = useTasks();
  const { taskFormModal } = useTaskModals();

  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<TaskFilters>({ status: 'all', providerName: 'all' });
  const [activeTab, setActiveTab] = useState('all');

  const quickStats = useMemo(() => ({
    total: tasks.length,
    active: tasks.filter(t => t.isActive).length,
    inactive: tasks.filter(t => !t.isActive).length,
  }), [tasks]);

  const filteredTasks = useMemo(() => {
    let filtered = [...tasks];

    if (activeTab === 'active') {
      filtered = filtered.filter(t => t.isActive);
    } else if (activeTab === 'inactive') {
      filtered = filtered.filter(t => !t.isActive);
    }

    if (searchText) {
      const lower = searchText.toLowerCase();
      filtered = filtered.filter(t => t.name.toLowerCase().includes(lower));
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(t => t.isActive === (filters.status === 'active'));
    }

    if (filters.providerName !== 'all') {
      filtered = filtered.filter(t => t.providerName === filters.providerName);
    }

    return filtered;
  }, [tasks, searchText, filters, activeTab]);

  if (error) return <QueryError title='Ошибка загрузки задач' error={error} />;

  return (
    <div style={{ margin: '0 auto' }}>
      <TaskStatsCards {...quickStats} />

      <TaskFilterPanel
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
            <Button type="primary" icon={<PlusOutlined />} onClick={() => taskFormModal()}>Добавить задачу</Button>
          </Space>
        }
        items={[
          { key: 'all', label: 'Все задачи' },
          { key: 'active', label: <span>Активные <Badge count={quickStats.active} style={{ backgroundColor: '#52c41a' }} /></span> },
          { key: 'inactive', label: <span>Неактивные <Badge count={quickStats.inactive} style={{ backgroundColor: '#ff4d4f' }} /></span> },
        ]}
      />

      <TaskTable data={filteredTasks} loading={isLoading} />
    </div>
  );
};
