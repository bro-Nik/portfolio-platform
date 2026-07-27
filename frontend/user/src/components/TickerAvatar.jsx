import React from 'react';
import { Avatar } from 'antd';

const TickerAvatar = ({ src, symbol, size = 24, style }) => {
  if (src) {
    return <Avatar src={src} size={size} style={{ minWidth: size, ...style }} />;
  }

  return (
    <Avatar
      size={size}
      style={{
        backgroundColor: '#1890ff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: size <= 24 ? 10 : 14,
        minWidth: size,
        ...style,
      }}
    >
      {symbol?.slice(0, 2).toUpperCase()}
    </Avatar>
  );
};

export default TickerAvatar;
