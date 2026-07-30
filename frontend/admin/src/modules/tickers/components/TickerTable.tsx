import React from 'react';
import { Tag, Dropdown, Button, Switch } from 'antd';
import Table from 'src/components/Table';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import { DeleteOutlined, EditOutlined, MergeCellsOutlined, MoreOutlined } from '@ant-design/icons';
import { Ticker } from '../../../types/ticker';
import { formatRelativeTime } from '../../../utils/date';
import { useTickerModals } from '../hooks/useTickerModals';
import { useTickerActions } from '../hooks/useTickerActions';

interface TickerTableProps { data: Ticker[]; loading: boolean; page: number; pageSize: number; total: number; onPageChange: (page: number) => void }

export const TickerTable: React.FC<TickerTableProps> = ({ data, loading, page, pageSize, total, onPageChange }) => {
  const { editModal, deleteConfirmModal } = useTickerModals();
  const { updateTicker, isUpdating } = useTickerActions();

  const columns: ColumnsType<Ticker> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Ticker) => (
        <Button type="link" onClick={() => editModal(record)} style={{ padding: 0 }}>
          <strong>{name}</strong>
        </Button>
      ),
    },
    {
      title: 'Символ',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: 'Рынок',
      dataIndex: 'market',
      key: 'market',
      width: 100,
      render: (market: string) => <Tag>{market}</Tag>,
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
      width: 120,
      render: (price: number) => price ? `$${price.toLocaleString()}` : '-',
    },
    {
      title: 'Rank',
      dataIndex: 'marketCapRank',
      key: 'marketCapRank',
      width: 60,
    },
    {
      title: 'Активен',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 90,
      render: (active: boolean, record: Ticker) => (
        <Switch
          size="small"
          checked={active}
          loading={isUpdating}
          onChange={(checked) => updateTicker(record.id, { isActive: checked })}
        />
      ),
    },
    {
      title: 'Цена от',
      dataIndex: 'priceUpdatedBy',
      key: 'priceUpdatedBy',
      width: 120,
      render: (v: string) => v ? <Tag color="blue">{v}</Tag> : '-',
    },
    {
      title: 'Обновлён',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 120,
      render: (date: string) => date ? formatRelativeTime(date) : '-',
    },
    {
      key: 'actions',
      width: 80,
      fixed: 'right',
      render: (_: unknown, record: Ticker) => {
        const menuItems: MenuProps['items'] = [
          {
            key: 'edit',
            label: 'Редактировать',
            icon: <EditOutlined />,
            onClick: () => editModal(record),
          },
          { type: 'divider' },
          {
            key: 'delete',
            label: 'Удалить',
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => deleteConfirmModal(record),
          },
        ];
        return (
          <Dropdown menu={{ items: menuItems }} placement="bottomRight" trigger={['click']}>
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        );
      },
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="id"
      loading={loading}
      pagination={{
        current: page,
        pageSize,
        total,
        onChange: onPageChange,
        showSizeChanger: false,
      }}
    />
  );
};
