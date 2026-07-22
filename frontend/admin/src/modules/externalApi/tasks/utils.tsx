import { Tag, Badge } from 'antd';
import { SyncOutlined, DatabaseOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons';

const taskTypeColors: Record<string, string> = {
  prices: 'blue',
  stats: 'green',
  markets: 'orange',
  default: 'default',
};

const taskTypeIcons: Record<string, React.ReactElement> = {
  prices: <DollarOutlined />,
  stats: <DatabaseOutlined />,
  markets: <RiseOutlined />,
  default: <SyncOutlined />,
};

export const getTaskTypeTag = (type: string): React.ReactElement => {
  const color = taskTypeColors[type] || taskTypeColors.default;
  const icon = taskTypeIcons[type] || taskTypeIcons.default;
  return <Tag icon={icon} color={color}>{type}</Tag>;
};

export const getStatusBadge = (status: boolean): React.ReactElement => {
  return status ? (
    <Badge status="success" text="Активна" />
  ) : (
    <Badge status="error" text="Неактивна" />
  );
};


