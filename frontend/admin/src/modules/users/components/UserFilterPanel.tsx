import React from 'react';
import { Card, Row, Col, Input, Select, Space, Button } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';
import { statuses, roles } from '../constants';
import { UserFilters } from '../../../types/user';

interface UserFilterPanelProps {
  filters: UserFilters;
  setFilters: (filters: UserFilters) => void;
  searchText: string;
  setSearchText: (text: string) => void;
}

export const UserFilterPanel: React.FC<UserFilterPanelProps> = ({ filters, setFilters, searchText, setSearchText }) => (
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
          setFilters({ status: 'all', role: 'all' });
          setSearchText('');
        }}
      >
        Сбросить все
      </Button>
    }
  >
    <Row gutter={[16, 8]} align="middle">
      <Col xs={24} md={12}>
        <Input
          placeholder="Поиск..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ width: '100%' }}
        />
      </Col>
      <Col xs={24} md={6}>
        <Select
          placeholder="Статус"
          style={{ width: '100%' }}
          value={filters.status}
          onChange={(value) => setFilters({ ...filters, status: value })}
          allowClear
        >
          <Select.Option value="all">Все статусы</Select.Option>
          {statuses.map(s => (
            <Select.Option key={s.value} value={s.value}>{s.label}</Select.Option>
          ))}
        </Select>
      </Col>
      <Col xs={24} md={6}>
        <Select
          placeholder="Роль"
          style={{ width: '100%' }}
          value={filters.role}
          onChange={(value) => setFilters({ ...filters, role: value })}
          allowClear
        >
          <Select.Option value="all">Все роли</Select.Option>
          {roles.map(r => (
            <Select.Option key={r.value} value={r.value}>{r.label}</Select.Option>
          ))}
        </Select>
      </Col>
    </Row>
  </Card>
);
