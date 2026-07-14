import React from 'react';
import { Spin } from 'antd';

const LoadingSpinner = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', height: '100%' }}>
    <Spin size="large" />
  </div>
);

export default LoadingSpinner;
