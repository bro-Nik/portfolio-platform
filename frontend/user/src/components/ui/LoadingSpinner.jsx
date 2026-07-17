import { Spin } from 'antd';

const LoadingSpinner = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', width: '100%' }}>
    <Spin size="large" />
  </div>
);

export default LoadingSpinner;
