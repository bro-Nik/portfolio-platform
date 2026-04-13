import { Tag } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';

export const getStatusTag = (isActive: boolean): React.ReactElement => {
  return isActive ? (
    <Tag icon={<CheckCircleOutlined />} color="success">Активен</Tag>
  ) : (
    <Tag icon={<CloseCircleOutlined />} color="error">Неактивен</Tag>
  );
};

export const getUtilizationColor = (percent: number): string => {
  if (percent < 50) return '#52c41a';
  if (percent < 80) return '#faad14';
  return '#ff4d4f';
};
