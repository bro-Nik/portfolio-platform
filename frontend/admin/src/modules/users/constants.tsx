import {
  UserAddOutlined,
  EyeOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  CrownOutlined,
  SafetyOutlined,
} from '@ant-design/icons';

export interface UserStatusOption {
  value: string;
  label: string;
  color: string;
  icon: React.ReactElement;
}

export interface UserRoleOption {
  value: string;
  label: string;
  color: string;
  icon: React.ReactElement;
}

export const statuses: UserStatusOption[] = [
  { value: 'active', label: 'Активен', color: 'green', icon: <CheckCircleOutlined /> },
  { value: 'inactive', label: 'Неактивен', color: 'red', icon: <CheckCircleOutlined /> },
  { value: 'block', label: 'Заблокирован', color: 'orange', icon: <CloseCircleOutlined /> },
  { value: 'pending', label: 'Ожидает', color: 'blue', icon: <ClockCircleOutlined /> },
];

export const roles: UserRoleOption[] = [
  { value: 'admin', label: 'Администратор', color: 'red', icon: <CrownOutlined /> },
  { value: 'moderator', label: 'Модератор', color: 'blue', icon: <SafetyOutlined /> },
  { value: 'editor', label: 'Редактор', color: 'green', icon: <EditOutlined /> },
  { value: 'viewer', label: 'Наблюдатель', color: 'purple', icon: <EyeOutlined /> },
  { value: 'user', label: 'Пользователь', color: 'default', icon: <UserAddOutlined /> },
];

export const avatars = [
  'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Jane',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Max',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Anna',
  'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike',
];
