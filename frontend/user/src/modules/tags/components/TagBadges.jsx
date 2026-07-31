import React from 'react';
import { Tag as AntTag, Tooltip } from 'antd';
import TagManagerSelect from './TagManagerSelect';

const MAX_VISIBLE = 3;

const TagBadges = ({ tags = [], size = 'small', entityType, entityId, parentId, assignedTags }) => {
  if (!tags || tags.length === 0) return null;

  const visible = tags.slice(0, MAX_VISIBLE);
  const overflow = tags.length - MAX_VISIBLE;

  const badges = (
    <span style={{ display: 'inline-flex', gap: 4, flexWrap: 'wrap', alignItems: 'center', lineHeight: 1.2, cursor: entityType && entityId ? 'pointer' : 'default' }}>
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

  if (entityType && entityId) {
    return (
      <TagManagerSelect
        trigger="inline"
        entityType={entityType}
        entityId={entityId}
        assignedTags={assignedTags || tags}
        parentId={parentId}
      >
        {badges}
      </TagManagerSelect>
    );
  }

  return badges;
};

export default TagBadges;
