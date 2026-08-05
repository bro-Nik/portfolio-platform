import React, { useState } from 'react';
import { Select, Tooltip } from 'antd';
import AntTag from 'antd/es/tag';
import { useTagsQuery } from '../hooks/useTagsQuery';

const TagFilter = ({ onChange, scope }) => {
  const { data: allTags = [] } = useTagsQuery();
  const [selectedIds, setSelectedIds] = useState([]);

  const handleChange = (values) => {
    setSelectedIds(values);
    onChange?.(values);
  };

  const tags = scope ? allTags.filter(t => t.scope === scope) : allTags;

  if (tags.length === 0) return null;

  return (
    <Select
      mode="multiple"
      maxTagCount={3}
      placeholder="Теги"
      value={selectedIds}
      onChange={handleChange}
      allowClear
      variant="filled"
      style={{ minWidth: 150 }}
      tagRender={({ value, label, closable, onClose, isMaxTag }) => {
        if (isMaxTag) {
          return (
            <AntTag style={{ marginRight: 4, fontSize: 12, lineHeight: '18px' }}>
              {label}
            </AntTag>
          );
        }
        const tag = tags.find(t => t.id === value);
        return (
          <AntTag color={tag?.color || '#1890ff'} closable={closable} onClose={onClose} style={{ marginRight: 4, fontSize: 12, lineHeight: '18px' }}>
            {tag?.name || value}
          </AntTag>
        );
      }}
      maxTagPlaceholder={(omittedValues) => {
        const names = omittedValues
          .map(v => tags.find(t => t.id === v.value)?.name)
          .filter(Boolean)
          .join(', ');
        return <Tooltip title={names}>+{omittedValues.length}</Tooltip>;
      }}
      options={tags.map(tag => ({
        value: tag.id,
        label: (
          <AntTag color={tag.color || '#1890ff'} style={{ margin: 0, fontSize: 12, lineHeight: '18px' }}>
            {tag.name}
          </AntTag>
        ),
      }))}
    />
  );
};

export default TagFilter;
