import React from 'react';
import { Button } from 'antd';
import { Inbox } from 'lucide-react';

const EmptyState = ({ icon: Icon = Inbox, title, description, action }) => {
  const iconSize = 36;
  return (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', padding: '64px 24px' }}>
    <div style={{ marginBottom: 20, color: 'var(--ant-color-text-tertiary)' }}>
      <Icon size={iconSize} strokeWidth={1.5} style={{ width: iconSize, height: iconSize }} />
    </div>
    <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8, color: 'var(--ant-color-text)' }}>
      {title}
    </div>
    {description && (
      <div style={{ fontSize: 14, color: 'var(--ant-color-text-secondary)', marginBottom: 24, lineHeight: 1.5 }}>
        {description}
      </div>
    )}
    {action && (
      <div style={{ marginTop: description ? 0 : 24 }}>
        <Button type="primary" onClick={action.onClick}>
          {action.text}
        </Button>
      </div>
    )}
  </div>
  );
};

export default EmptyState;
