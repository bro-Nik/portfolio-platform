import React from 'react';
import { Card, Col, Input, Row, Select, Space, Button } from 'antd';
import { FilterOutlined, SearchOutlined } from '@ant-design/icons';

export interface ProviderFilters {
  status: string;
}

interface ProviderFilterPanelProps {
  filters: ProviderFilters;
  setFilters: (filters: ProviderFilters) => void;
  searchText: string;
  setSearchText: (text: string) => void;
}

export const ProviderFilterPanel: React.FC<ProviderFilterPanelProps> = ({
  filters,
  setFilters,
  searchText,
  setSearchText,
}) => (
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
          setFilters({ status: 'all' });
          setSearchText('');
        }}
      >
        Сбросить
      </Button>
    }
  >
    <Row gutter={[16, 8]} align="middle">
      <Col xs={24} md={16}>
        <Input
          placeholder="Поиск по названию..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ width: '100%' }}
        />
      </Col>
      <Col xs={24} md={8}>
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
    </Row>
  </Card>
);
