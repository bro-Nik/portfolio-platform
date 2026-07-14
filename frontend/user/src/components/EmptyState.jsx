import React from 'react';
import { Empty } from 'antd';

const EmptyState = () => (
  <div style={{ gridColumn: '1 / -1' }}>
    <Empty description="Пока ничего нет..." />
  </div>
);

export default EmptyState;
