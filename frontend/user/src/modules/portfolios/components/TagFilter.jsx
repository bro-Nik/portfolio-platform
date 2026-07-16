import React, { useState, useEffect } from 'react';
import { Select, Space } from 'antd';
import { tagApi } from '../api/tagApi';

const TagFilter = ({ onChange }) => {
  const [allTags, setAllTags] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await tagApi.getTags();
        setAllTags(data);
      } catch (error) {
        console.warn('Ошибка загрузки тегов:', error);
      }
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
