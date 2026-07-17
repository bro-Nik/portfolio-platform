import React, { useState } from 'react';
import { Select } from 'antd';
import { useTagsQuery } from '../../../hooks/queries/useTagsQuery';

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
      placeholder="Теги"
      value={selectedIds}
      onChange={handleChange}
      allowClear
      style={{ minWidth: 150 }}
      options={allTags.map(tag => ({
        value: tag.id,
        label: (
          <span>
            <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', backgroundColor: tag.color || '#1890ff', marginRight: 6 }} />
            {tag.name}
          </span>
        ),
      }))}
    />
  );
};

export default TagFilter;
