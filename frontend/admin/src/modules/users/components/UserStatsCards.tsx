import React from 'react';
import { Card, Row, Col, Badge, Statistic } from 'antd';
import { TeamOutlined, CheckCircleOutlined, CrownOutlined, StarOutlined } from '@ant-design/icons';
import { UserStats } from '/app/src/types/user';

interface UserStatsCardsProps {
  quickStats: UserStats;
}

export const UserStatsCards: React.FC<UserStatsCardsProps> = ({ quickStats }) => (
  <Row gutter={[16, 16]}>
    <Col xs={24} sm={6} md={6} lg={4}>
      <Card size="small" hoverable>
        <Statistic
          title="Всего"
          value={quickStats.total}
          prefix={<TeamOutlined />}
          styles={{ content: { color: '#1890ff' } }}
        />
      </Card>
    </Col>

    <Col xs={24} sm={6} md={6} lg={4}>
      <Card size="small" hoverable>
        <Statistic
          title="Активных"
          value={quickStats.active}
          prefix={<CheckCircleOutlined />}
          styles={{ content: { color: '#52c41a' } }}
        />
      </Card>
    </Col>

    <Col xs={24} sm={6} md={6} lg={4}>
      <Card size="small" hoverable>
        <Statistic
          title="Онлайн"
          value={quickStats.online}
          prefix={<Badge status="success" />}
          styles={{ content: { color: '#722ed1' } }}
        />
      </Card>
    </Col>

    <Col xs={24} sm={6} md={6} lg={4}>
      <Card size="small" hoverable>
        <Statistic
          title="Админов"
          value={quickStats.admins}
          prefix={<CrownOutlined />}
          styles={{ content: { color: '#fa541c' } }}
        />
      </Card>
    </Col>

    <Col xs={24} sm={6} md={6} lg={4}>
      <Card size="small" hoverable>
        <Statistic
          title="Новых за 30 дней"
          value={quickStats.newMonth}
          prefix={<StarOutlined />}
          styles={{ content: { color: '#faad14' } }}
        />
      </Card>
    </Col>
  </Row>
);
