import React from 'react';
import { Card, Col, Row, Statistic } from 'antd';
import { ApiOutlined, CheckCircleOutlined, CloseCircleOutlined, RocketOutlined } from '@ant-design/icons';

interface ProviderStatsCardsProps {
  total: number;
  active: number;
  inactive: number;
  withCounters: number;
}

export const ProviderStatsCards: React.FC<ProviderStatsCardsProps> = ({ total, active, inactive, withCounters }) => (
  <Row gutter={[16, 16]}>
    <Col xs={24} sm={12} md={6}>
      <Card size="small" hoverable>
        <Statistic
          title="Всего"
          value={total}
          prefix={<ApiOutlined />}
          styles={{ content: { color: '#1890ff' } }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} md={6}>
      <Card size="small" hoverable>
        <Statistic
          title="Активных"
          value={active}
          prefix={<CheckCircleOutlined />}
          styles={{ content: { color: '#52c41a' } }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} md={6}>
      <Card size="small" hoverable>
        <Statistic
          title="Неактивных"
          value={inactive}
          prefix={<CloseCircleOutlined />}
          styles={{ content: { color: '#ff4d4f' } }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} md={6}>
      <Card size="small" hoverable>
        <Statistic
          title="С счётчиками"
          value={withCounters}
          prefix={<RocketOutlined />}
          styles={{ content: { color: '#722ed1' } }}
        />
      </Card>
    </Col>
  </Row>
);
