import { Tag, Space } from 'antd';
import { UserAddOutlined } from '@ant-design/icons';
import { roles, avatars, statuses } from './constants';
import { User } from '/app/src/types/user';

export const getUserRoleTag = (role: string): React.ReactElement => {
  const roleData = roles.find(r => r.value === role);

  return (
    <Tag
      color={roleData?.color || 'default'}
      icon={roleData?.icon || <UserAddOutlined />}
    >
      {roleData?.label || role}
    </Tag>
  );
};

export const getUserAvatar = (user: User | null | undefined): string => {
  return avatars[(user?.id ?? 0) % avatars.length];
};

export const getUserStatusTag = (status: string): React.ReactElement => {
  const statusData = statuses.find(s => s.value === status);

  return (
    <Space>
      <Tag
        color={statusData?.color || 'default'}
        icon={statusData?.icon}
      >
        {statusData?.label || status}
      </Tag>
    </Space>
  );
};
