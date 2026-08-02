import { Alert } from '@portfolio/shared';
import { Modal, Tabs, Row, Col, Card, Statistic, Progress, Space, Descriptions, Tag, Timeline, Button } from 'antd';
import {
  BarChartOutlined,
  HistoryOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  KeyOutlined
} from '@ant-design/icons';
import { getStatusTag } from '../utils';
import { providersApi } from '../api';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useModalProps, useModalStore } from '@portfolio/shared';
import { LoadingSpinner } from '../../../../components/LoadingSpinner';
import { Provider } from '../../../../types/provider';
import { useProviderActions } from '../hooks/useProviderActions';

interface ProviderDetailsModalProps { provider: Provider }
interface ProviderInfoTabProps { provider: Provider }
interface ProviderStatsTabProps { providerName: string }
interface ProviderLogsTabProps { providerName: string }

export const ProviderDetailsModal: React.FC = () => {
  const { closeModal } = useModalStore();
  const { provider } = useModalProps<ProviderDetailsModalProps>();

  if (!provider) return null;

  return (
    <Modal
      title={`Статистика API провайдера: ${provider.name}`}
      open={true}
      onCancel={closeModal}
      footer={null}
      width={800}
    >
      <Tabs
        defaultActiveKey="info"
        items={[
          { key: 'info', label: 'Информация', icon: <SafetyOutlined />, children: <ProviderInfoTab provider={provider}/> },
          { key: 'stats', label: 'Статистика', icon: <BarChartOutlined />, children: <ProviderStatsTab providerName={provider.name} /> },
          { key: 'logs', label: 'История запросов', icon: <HistoryOutlined />, children: <ProviderLogsTab providerName={provider.name} /> },
        ]}
      />
    </Modal>
  );
};

const ProviderInfoTab: React.FC<ProviderInfoTabProps> = ({ provider }) => {
  return (
    <Descriptions bordered column={1}>
      <Descriptions.Item label="Название">
        {provider.name}
      </Descriptions.Item>

      {provider.description && (
        <Descriptions.Item label="Описание">
          {provider.description}
        </Descriptions.Item>
      )}

      <Descriptions.Item label="API Ключ">
        {provider.apiKey ? (
          <Tag color="green" icon={<KeyOutlined />}>Настроен</Tag>
        ) : (
          <Tag color="orange">Не настроен</Tag>
        )}
      </Descriptions.Item>

      <Descriptions.Item label="Таймаут">
        {provider.timeout} секунд
      </Descriptions.Item>

      <Descriptions.Item label="Задержка повтора">
        {provider.retryDelay} секунд
      </Descriptions.Item>

      <Descriptions.Item label="Статус">
        {getStatusTag(provider.isActive ?? false)}
      </Descriptions.Item>
    </Descriptions>
  );
};

const ProviderStatsTab: React.FC<ProviderStatsTabProps> = ({ providerName }) => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['providerStats', providerName],
    queryFn: () => providersApi.getProviderStats(providerName),
  });

  const { resetProviderCounters } = useProviderActions();

  if (isLoading) return <LoadingSpinner size={48}/>;
  if (error) return <Alert title="Ошибка" description={error.message} type="error" />;
  if (!stats) return <Alert title="Нет данных" description="Статистика не загружена" type="info" />;

  return (
    <>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Запросов сегодня"
              value={stats.requestsToday}
              prefix={<ThunderboltOutlined />}
              styles={{ content: { color: '#1890ff' } }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Успешных"
              value={stats.successfulToday}
              prefix={<CheckCircleOutlined />}
              styles={{ content: { color: '#52c41a' } }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="Ошибок"
              value={stats.failedToday}
              prefix={<CloseCircleOutlined />}
              styles={{ content: { color: '#ff4d4f' } }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Использование лимитов" size="small">
        <Space vertical style={{ width: '100%' }}>
          {Object.entries(stats.utilizationPercent || {}).map(([key, percent]) => {
            const p = percent as number;
            return (
            <div key={key}>
              <span>{key.charAt(0).toUpperCase() + key.slice(1)}:</span>
              <Progress 
                percent={Math.round(p)}
                status={p > 80 ? 'exception' : 'normal'}
                format={() => {
                  const statsRecord = stats as unknown as Record<string, number | undefined>;
                  const counter = statsRecord[`${key}Counter`];
                  const limit = statsRecord[`${key}Limit`];
                  return `${counter ?? '-'}/${limit ?? '-'}`;
                }}
              />
            </div>
          );
          })}
        </Space>
      </Card>

      <Card title="Общая информация" size="small" style={{ marginTop: '16px' }}>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="Среднее время ответа">
            {stats.avgResponseTime ? 
              `${stats.avgResponseTime.toFixed(2)}с` : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <div style={{ textAlign: 'center', marginTop: '16px' }}>
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={() => resetProviderCounters(providerName)}
        >
          Сбросить все счетчики
        </Button>
      </div>
    </>
  );
};


const ProviderLogsTab: React.FC<ProviderLogsTabProps> = ({ providerName }) => {
  const [hours] = useState(24);
  const { data: logs, isLoading, error } = useQuery({
    queryKey: ['providerLogs', providerName, hours],
    queryFn: () => providersApi.getProviderLogs(providerName),
  });

  if (isLoading) return <LoadingSpinner size={48}/>;
  if (error) return <Alert title="Ошибка" description={error.message} type="error" />;
  if (!logs || logs.length === 0) return <Alert title="Нет данных" description="За последние 24 часа не было запросов" type="info" />;

  return (
    <Timeline>
      {logs.map((log, index) => (
        <Timeline.Item key={log.id || index} color={log.wasSuccessful ? "green" : "red"}>
          <Space vertical size={0}>
            <div>
              <strong>{log.endpoint}</strong>
              <Tag color={log.wasSuccessful ? "success" : "error"} style={{ marginLeft: '8px' }}>
                {log.statusCode || 'ERROR'}
              </Tag>
            </div>
            <div>
              <span style={{ fontSize: '12px', color: 'var(--text-admin-secondary)' }}>
                {new Date(log.createdAt).toLocaleString()}
              </span>
              <Tag style={{ marginLeft: '8px', fontSize: '12px' }}>
                {log.responseTime?.toFixed(2)}с
              </Tag>
            </div>
            {log.errorMessage && (
              <Alert title={log.errorMessage} type="error" />
            )}
          </Space>
        </Timeline.Item>
      ))}
    </Timeline>
  );
};
