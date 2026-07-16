import { Modal, Tabs, Row, Col, Card, Statistic, Progress, Space, Descriptions, Tag, Timeline, Alert, Button } from 'antd';
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
import { useQuery } from '@tanstack/react-query';
import { useModalStore } from '@portfolio/shared';
import { LoadingSpinner } from '../../../../components/LoadingSpinner';
import { Provider } from '../../../../types/provider';
import { useProviderActions } from '../hooks/useProviderActions';

interface ProviderDetailsModalProps { provider: Provider }
interface ProviderInfoTabProps { provider: Provider }
interface ProviderStatsTabProps { providerId: number }
interface ProviderLogsTabProps { providerId: number }

const { TabPane } = Tabs;

export const ProviderDetailsModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { provider }: ProviderDetailsModalProps = modalProps;

  if (!provider) return null;

  return (
    <Modal
      title={`Статистика API провайдера: ${provider.name}`}
      open={true}
      onCancel={closeModal}
      footer={null}
      width={800}
    >
      <Tabs defaultActiveKey="info">
        <TabPane tab="Информация" key="info" icon={<SafetyOutlined />}>
          <ProviderInfoTab provider={provider}/>
        </TabPane>

        <TabPane tab="Статистика" key="stats" icon={<BarChartOutlined />}>
          <ProviderStatsTab providerId={provider.id} />
        </TabPane>

        <TabPane tab="История запросов" key="logs" icon={<HistoryOutlined />}>
          <ProviderLogsTab providerId={provider.id} />
        </TabPane>
      </Tabs>
    </Modal>
  );
};

const ProviderInfoTab: React.FC<ProviderInfoTabProps> = ({ provider }) => {
  return (
    <Descriptions bordered column={1}>
      <Descriptions.Item label="Название">
        {provider.name}
      </Descriptions.Item>

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
        {getStatusTag(provider.isActive)}
      </Descriptions.Item>
    </Descriptions>
  );
};

const ProviderStatsTab: React.FC<ProviderStatsTabProps> = ({ providerId }) => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['providerStats', providerId],
    queryFn: () => providersApi.getProviderStats(providerId),
  });

  const { resetProviderCounters } = useProviderActions();

  if (isLoading) return <LoadingSpinner size={48}/>;
  if (error) return <Alert title="Ошибка" description={error.message} type="error" showIcon />;
  if (!stats) return <Alert title="Нет данных" description="Статистика не загружена" type="info" showIcon />;

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
                  const counter = stats[`${key}Counter`];
                  const limit = stats[`${key}Limit`];
                  return `${counter}/${limit}`;
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
          onClick={() => resetProviderCounters(providerId)}
        >
          Сбросить все счетчики
        </Button>
      </div>
    </>
  );
};


const ProviderLogsTab: React.FC<ProviderLogsTabProps> = ({ providerId }) => {
  const { data: logs, isLoading, error } = useQuery({
    queryKey: ['providerLogs', providerId],
    queryFn: () => providersApi.getProviderLogs(providerId),
  });

  if (isLoading) return <LoadingSpinner size={48}/>;
  if (error) return <Alert title="Ошибка" description={error.message} type="error" showIcon />;
  if (!logs || logs.length === 0) return <Alert title="Нет данных" description="За последние 24 часа не было запросов" type="info" showIcon />;

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
              <span style={{ fontSize: '12px', color: '#666' }}>
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
