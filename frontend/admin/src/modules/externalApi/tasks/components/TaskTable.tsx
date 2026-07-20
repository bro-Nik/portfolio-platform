import React from 'react';
import { Table, Tag, Dropdown, Button, Tooltip } from 'antd';
import { ScheduleOutlined, ApiOutlined, DeleteOutlined, MoreOutlined, EditOutlined, EyeOutlined, PlayCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { MenuProps } from 'antd';
import { schedulePresets } from '../constants';
import { formatRelativeTime } from '../../../../utils/date';
import { Task } from '../../../../types/task';
import { useTaskModals } from '../hooks/useTaskModals';
import { useTaskActions } from '../hooks/useTaskActions';
import { getTaskTypeTag, getStatusBadge } from '../utils';

interface TaskTableProps { data: Task[]; loading: boolean }

export const TaskTable: React.FC<TaskTableProps> = ({ data, loading }) => {
  const { taskDetailsModal, taskFormModal, taskDeleteConfirmModal } = useTaskModals();
  const { runTask, isRunning } = useTaskActions();

  const columns: ColumnsType<Task> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Task) => (
        <Button type="link" onClick={() => taskDetailsModal(record)} style={{ padding: 0 }}>
          <strong>{name}</strong>
        </Button>
      )
    },
    {
      title: 'Провайдер',
      dataIndex: 'providerName',
      key: 'providerName',
      width: 160,
      render: (_: unknown, record: Task) => (
        <Tag icon={<ApiOutlined />} color="green">{record.providerName || '—'}</Tag>
      )
    },
    {
      title: 'Тип задачи',
      dataIndex: 'taskType',
      key: 'type',
      render: (type: string) => getTaskTypeTag(type)
    },
    {
      title: 'Расписание',
      dataIndex: 'schedule',
      key: 'schedule',
      render: (schedule: string) => (
        schedule ? (
          <Tooltip title={schedule}>
            <Tag icon={<ScheduleOutlined />} color="purple">
              {schedulePresets.find(p => p.value === schedule)?.label || schedule}
            </Tag>
          </Tooltip>
        ) : (
          <Tag color="orange">Вручную</Tag>
        )
      )
    },
    {
      title: 'Активность',
      dataIndex: 'isActive',
      key: 'isActive',
      render: (status: boolean) => getStatusBadge(status)
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => status || '-'
    },
    {
      title: 'Последний запуск',
      dataIndex: 'lastRun',
      key: 'lastRun',
      render: (date: string) => date ? formatRelativeTime(date) : '-'
    },
    {
      title: 'Следующий запуск',
      dataIndex: 'nextRun',
      key: 'nextRun',
      render: (date: string) => date ? formatRelativeTime(date) : '-'
    },
    {
      key: 'actions',
      width: 80,
      fixed: 'right',
      render: (_: unknown, record: Task) => {
        const menuItems: MenuProps['items'] = [
          {
            key: 'view',
            label: 'Подробнее',
            icon: <EyeOutlined />,
            onClick: () => taskDetailsModal(record)
          },
          {
            key: 'edit',
            label: 'Редактировать',
            icon: <EditOutlined />,
            onClick: () => taskFormModal(record)
          },
          {
            key: 'run',
            label: 'Запустить сейчас',
            icon: <PlayCircleOutlined />,
            disabled: isRunning,
            onClick: () => runTask(record.id)
          },
          { type: 'divider' },
          {
            key: 'delete',
            label: 'Удалить',
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => taskDeleteConfirmModal(record)
          }
        ];

        return (
          <Dropdown menu={{ items: menuItems }} placement="bottomRight" trigger={['click']}>
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        );
      }
    }
  ]

  return <Table columns={columns} dataSource={data} rowKey="id" loading={loading} pagination={{ pageSize: 10 }} scroll={{ x: 1100 }} />;
};
