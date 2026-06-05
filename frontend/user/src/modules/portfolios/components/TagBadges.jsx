import React from 'react';
import { Tag as AntTag, Tooltip } from 'antd';

const MAX_VISIBLE = 3;

const TagBadges = ({ tags = [], size = 'small' }) => {
  if (!tags || tags.length === 0) return null;

  const visible = tags.slice(0, MAX_VISIBLE);
  const overflow = tags.length - MAX_VISIBLE;

  return (
    <span className="d-inline-flex gap-1 flex-wrap align-items-center" style={{ lineHeight: 1.2 }}>
      {visible.map(tag => (
        <AntTag key={tag.id} color={tag.color || '#1890ff'} style={{ margin: 0, fontSize: size === 'small' ? 10 : 12, lineHeight: '16px' }}>
          {tag.name}
        </AntTag>
      ))}
      {overflow > 0 && (
        <Tooltip title={tags.slice(MAX_VISIBLE).map(t => t.name).join(', ')}>
          <AntTag style={{ margin: 0, fontSize: 10, lineHeight: '16px' }}>+{overflow}</AntTag>
        </Tooltip>
      )}
    </span>
  );
};

export default TagBadges;
