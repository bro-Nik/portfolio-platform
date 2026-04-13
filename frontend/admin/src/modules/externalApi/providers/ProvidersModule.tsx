import React, { useState, useMemo } from 'react';
import { Badge, Button, Space, Tabs } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { ProviderTable } from './components/ProviderTable';
import { ProviderFilterPanel, ProviderFilters } from './components/ProviderFilterPanel';
import { ProviderStatsCards } from './components/ProviderStatsCards';
import { useProviders } from './hooks/useProviders';
import { useProviderModals } from './hooks/useProviderModals';
import { QueryError } from '/app/src/components/QueryError';

export const ProvidersModule: React.FC = () => {
  const { data: providers = [], isLoading, error } = useProviders();
  const { providerFormModal } = useProviderModals();

  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<ProviderFilters>({ status: 'all' });
  const [activeTab, setActiveTab] = useState('all');

  const quickStats = useMemo(() => ({
    total: providers.length,
    active: providers.filter(p => p.isActive).length,
    inactive: providers.filter(p => !p.isActive).length,
    withCounters: providers.filter(p => p.dayCounter > 0 || p.monthCounter > 0).length,
  }), [providers]);

  const filteredProviders = useMemo(() => {
    let filtered = [...providers];

    if (activeTab === 'active') {
      filtered = filtered.filter(p => p.isActive);
    } else if (activeTab === 'inactive') {
      filtered = filtered.filter(p => !p.isActive);
    }

    if (searchText) {
      const lower = searchText.toLowerCase();
      filtered = filtered.filter(p => p.name.toLowerCase().includes(lower));
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(p => p.isActive === (filters.status === 'active'));
    }

    return filtered;
  }, [providers, searchText, filters, activeTab]);

  if (error) return <QueryError title='Ошибка загрузки провайдеров' error={error} />;

  return (
    <div style={{ margin: '0 auto' }}>
      <ProviderStatsCards {...quickStats} />

      <ProviderFilterPanel
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
            <Button type="primary" icon={<PlusOutlined />} onClick={() => providerFormModal()}>Добавить провайдера</Button>
          </Space>
        }
      >
        <Tabs.TabPane tab="Все провайдеры" key="all" />
        <Tabs.TabPane
          tab={<span>Активные <Badge count={quickStats.active} style={{ backgroundColor: '#52c41a' }} /></span>}
          key="active"
        />
        <Tabs.TabPane
          tab={<span>Неактивные <Badge count={quickStats.inactive} style={{ backgroundColor: '#ff4d4f' }} /></span>}
          key="inactive"
        />
        <Tabs.TabPane
          tab={<span>С счётчиками <Badge count={quickStats.withCounters} style={{ backgroundColor: '#722ed1' }} /></span>}
          key="withCounters"
        />
      </Tabs>

      <ProviderTable data={filteredProviders} loading={isLoading} />
    </div>
  );
};
