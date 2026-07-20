import { Table, Space, Tag, Dropdown, Button, Progress } from 'antd';
import { ApiOutlined, EditOutlined, DeleteOutlined, MoreOutlined, ReloadOutlined, EyeOutlined, SettingOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import { getStatusTag, getUtilizationColor } from '../utils';
import { Provider } from '../../../../types/provider';
import { useProviderModals } from '../hooks/useProviderModals';
import { useProviderActions } from '../hooks/useProviderActions';

interface ProviderTableProps { data: Provider[]; loading: boolean }


export const ProviderTable: React.FC<ProviderTableProps> = ({ data, loading }) => {
  const { providerDetailsModal, providerFormModal, providerResetConfigConfirmModal } = useProviderModals();
  const { resetProviderCounters } = useProviderActions();

  const columns: ColumnsType<Provider> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      fixed: 'left',
      width: 180,
      render: (name: string, record: Provider) => (
        <Button type="link" onClick={() => providerDetailsModal(record)} style={{ padding: 0 }}>
          <ApiOutlined style={{ color: '#1890ff', marginRight: 4 }} />
          <strong>{name}</strong>
        </Button>
      )
    },
    {
      title: 'Статус',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 120,
      render: (isActive: boolean) => getStatusTag(isActive)
    },
    {
      title: 'Лимиты',
      key: 'limits',
      width: 220,
      render: (_: unknown, record: Provider) => (
        <Space vertical size="small">
          <span>
            {record.requestsPerMinute && <Tag color="blue">{record.requestsPerMinute}/мин</Tag>}
            {record.requestsPerHour && <Tag color="green">{record.requestsPerHour}/час</Tag>}
          </span>
          <span>
            {record.requestsPerDay && <Tag color="orange">{record.requestsPerDay}/день</Tag>}
            {record.requestsPerMonth && <Tag color="red">{record.requestsPerMonth}/мес</Tag>}
          </span>
        </Space>
      )
    },
    {
      title: 'Использование',
      key: 'usage',
      width: 260,
      render: (_: unknown, record: Provider) => {
        const dayPercent = record.requestsPerDay ? Math.min((record.dayCounter / record.requestsPerDay) * 100, 100) : 0;
        const monthPercent = record.requestsPerMonth ? Math.min((record.monthCounter / record.requestsPerMonth) * 100, 100) : 0;

        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '11px', color: 'var(--text-admin-secondary)', minWidth: 32, flexShrink: 0 }}>День:</span>
              <Progress
                percent={Math.round(dayPercent)}
                size="small"
                strokeColor={getUtilizationColor(dayPercent)}
                format={() => `${record.dayCounter}${record.requestsPerDay ? '/' + record.requestsPerDay : ''}`}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '11px', color: 'var(--text-admin-secondary)', minWidth: 32, flexShrink: 0 }}>Мес:</span>
              <Progress
                percent={Math.round(monthPercent)}
                size="small"
                strokeColor={getUtilizationColor(monthPercent)}
                format={() => `${record.monthCounter}${record.requestsPerMonth ? '/' + record.requestsPerMonth : ''}`}
              />
            </div>
          </div>
        );
      }
    },
    {
      key: 'actions',
      fixed: 'right',
      width: 80,
      render: (_: unknown, record: Provider) => {
        const items: MenuProps['items'] = [
          {
            key: 'view',
            label: 'Подробнее',
            icon: <EyeOutlined />,
            onClick: () => providerDetailsModal(record)
          },
          {
            key: 'counters',
            label: 'Сбросить счетчики',
            icon: <ReloadOutlined />,
            onClick: () => resetProviderCounters(record.name)
          },
          { type: 'divider' },
          {
            key: 'setup',
            label: 'Настроить',
            icon: <SettingOutlined />,
            onClick: () => providerFormModal(record)
          },
        ];

        if (record.hasConfig) {
          items.push({
            key: 'resetConfig',
            label: 'Сбросить конфиг',
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => providerResetConfigConfirmModal(record)
          });
        }

        return (
          <Dropdown menu={{ items }} placement="bottomRight" trigger={['click']}>
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        );
      }
    }
  ];

  return <Table columns={columns} dataSource={data} rowKey="name" loading={loading} pagination={{ pageSize: 10 }} scroll={{ x: 900 }} />;
};
