import React from 'react';
import { Card, Col, Input, Row, Select, Space, Button } from 'antd';
import { FilterOutlined, SearchOutlined } from '@ant-design/icons';
import { useProviders } from '../../providers/hooks/useProviders';

export interface TaskFilters {
  status: string;
  providerName: string;
}

interface TaskFilterPanelProps {
  filters: TaskFilters;
  setFilters: (filters: TaskFilters) => void;
  searchText: string;
  setSearchText: (text: string) => void;
}

export const TaskFilterPanel: React.FC<TaskFilterPanelProps> = ({ filters, setFilters, searchText, setSearchText }) => {
  const { data: providers = [], isLoading: providersLoading, error: providersError } = useProviders();

  return (
    <Card
      size="small"
      style={{ marginTop: '16px' }}
      title={
        <Space>
          <FilterOutlined />
          <span>Фильтры</span>
        </Space>
      }
      extra={
        <Button
          size="small"
          onClick={() => {
            setFilters({ status: 'all', providerName: 'all' });
            setSearchText('');
          }}
        >
          Сбросить
        </Button>
      }
    >
      <Row gutter={[16, 8]} align="middle">
        <Col xs={24} md={10}>
          <Input
            placeholder="Поиск по названию..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
            style={{ width: '100%' }}
          />
        </Col>
        <Col xs={24} md={7}>
          <Select
            placeholder="Статус"
            style={{ width: '100%' }}
            value={filters.status}
            onChange={(value) => setFilters({ ...filters, status: value })}
            allowClear
          >
            <Select.Option value="all">Все статусы</Select.Option>
            <Select.Option value="active">Активные</Select.Option>
            <Select.Option value="inactive">Неактивные</Select.Option>
          </Select>
        </Col>
        <Col xs={24} md={7}>
          <Select
            placeholder="Провайдер"
            style={{ width: '100%' }}
            value={filters.providerName}
            disabled={providersLoading || !!providersError}
            onChange={(value) => setFilters({ ...filters, providerName: value })}
            allowClear
          >
            <Select.Option value="all">Все провайдеры</Select.Option>
            {providers.map(p => (
              <Select.Option key={p.name} value={p.name}>{p.name}</Select.Option>
            ))}
          </Select>
        </Col>
      </Row>
    </Card>
  );

};
