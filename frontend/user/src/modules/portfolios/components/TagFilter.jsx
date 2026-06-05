import React, { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import { tagApi } from '../api/tagApi';

const TagFilter = ({ onChange }) => {
  const [allTags, setAllTags] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  useEffect(() => {
    const load = async () => {
      const result = await tagApi.getTags();
      if (result.success) setAllTags(result.data);
    };
    load();
  }, []);

  const handleChange = (values) => {
    setSelectedIds(values);
    onChange?.(values);
  };

  if (allTags.length === 0) return null;

  return (
    <Select
      mode="multiple"
      size="small"
      placeholder="Фильтр по тегам"
      value={selectedIds}
      onChange={handleChange}
      allowClear
      style={{ minWidth: 180, maxWidth: 300 }}
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
