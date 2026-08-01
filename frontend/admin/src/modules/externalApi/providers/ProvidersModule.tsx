import React, { useState, useMemo } from 'react';
import { Badge, Button, Space, Tabs } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { ProviderTable } from './components/ProviderTable';
import { ProviderFilterPanel, ProviderFilters } from './components/ProviderFilterPanel';
import { ProviderStatsCards } from './components/ProviderStatsCards';
import { useProviders } from './hooks/useProviders';
import { usePersistedState } from '@portfolio/shared';
import { QueryError } from '../../../components/QueryError';

export const ProvidersModule: React.FC = () => {
  const { data: providers = [], isLoading, error } = useProviders();

  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<ProviderFilters>({ status: 'all' });
  const [activeTab, setActiveTab] = usePersistedState('providers_tab', 'all');

  const quickStats = useMemo(() => ({
    total: providers.length,
    active: providers.filter(p => p.isActive).length,
    inactive: providers.filter(p => !p.isActive).length,
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
          </Space>
        }
        items={[
          { key: 'all', label: 'Все провайдеры' },
          { key: 'active', label: <span>Активные <Badge count={quickStats.active} style={{ backgroundColor: '#52c41a' }} /></span> },
          { key: 'inactive', label: <span>Неактивные <Badge count={quickStats.inactive} style={{ backgroundColor: '#ff4d4f' }} /></span> },
        ]}
      />

      <ProviderTable data={filteredProviders} loading={isLoading} />
    </div>
  );
};
