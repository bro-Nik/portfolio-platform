import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps { size?: number }

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 48 }) => (
  <div style={{ textAlign: 'center', padding: '50px' }}>
    <Spin indicator={<LoadingOutlined style={{ fontSize: size }} spin />} />
  </div>
);
