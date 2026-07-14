import React from 'react';
import { Space } from 'antd';

const StatisticCards = ({ cards }) => {
  return (
    <Space size="large" style={{ marginBottom: 24, display: 'flex', flexWrap: 'wrap' }}>
      {cards.map((card, index) => (
        <div key={index}>
          <p style={{ fontSize: '12px' }}>{card.title}</p>
          <span className={`text-average ${card.class || ''}`}>{card.value}</span>
        </div>
      ))}
    </Space>
  );
};

export default StatisticCards;
