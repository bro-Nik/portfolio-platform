import React, { useState } from 'react';
import { Select, Tooltip } from 'antd';
import AntTag from 'antd/es/tag';
import { useTagsQuery } from '../hooks/useTagsQuery';

const TagFilter = ({ onChange }) => {
  const { data: allTags = [] } = useTagsQuery();
  const [selectedIds, setSelectedIds] = useState([]);

  const handleChange = (values) => {
    setSelectedIds(values);
    onChange?.(values);
  };

  if (allTags.length === 0) return null;

  return (
    <Select
      mode="multiple"
      maxTagCount={3}
      placeholder="Теги"
      value={selectedIds}
      onChange={handleChange}
      allowClear
      style={{ minWidth: 150 }}
      tagRender={({ value, label, closable, onClose, isMaxTag }) => {
        if (isMaxTag) {
          return (
            <AntTag style={{ marginRight: 4, fontSize: 12, lineHeight: '18px' }}>
              {label}
            </AntTag>
          );
        }
        const tag = allTags.find(t => t.id === value);
        return (
          <AntTag color={tag?.color || '#1890ff'} closable={closable} onClose={onClose} style={{ marginRight: 4, fontSize: 12, lineHeight: '18px' }}>
            {tag?.name || value}
          </AntTag>
        );
      }}
      maxTagPlaceholder={(omittedValues) => {
        const names = omittedValues
          .map(v => allTags.find(t => t.id === v.value)?.name)
          .filter(Boolean)
          .join(', ');
        return <Tooltip title={names}>+{omittedValues.length}</Tooltip>;
      }}
      options={allTags.map(tag => ({
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
