import React from 'react';
import { Card, Col, Row, Statistic } from 'antd';
import { ApiOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';

interface ProviderStatsCardsProps {
  total: number;
  active: number;
  inactive: number;
}

export const ProviderStatsCards: React.FC<ProviderStatsCardsProps> = ({ total, active, inactive }) => (
  <Row gutter={[16, 16]}>
    <Col xs={24} sm={12} md={8}>
      <Card size="small" hoverable>
        <Statistic
          title="Всего"
          value={total}
          prefix={<ApiOutlined />}
          styles={{ content: { color: '#1890ff' } }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} md={8}>
      <Card size="small" hoverable>
        <Statistic
          title="Активных"
          value={active}
          prefix={<CheckCircleOutlined />}
          styles={{ content: { color: '#52c41a' } }}
        />
      </Card>
    </Col>
    <Col xs={24} sm={12} md={8}>
      <Card size="small" hoverable>
        <Statistic
          title="Неактивных"
          value={inactive}
          prefix={<CloseCircleOutlined />}
          styles={{ content: { color: '#ff4d4f' } }}
        />
      </Card>
    </Col>
  </Row>
);
