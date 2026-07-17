import { Spin } from 'antd';

interface LoadingSpinnerProps { size?: number }

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 48 }) => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200, width: '100%' }}>
    <Spin size="large" />
  </div>
);
