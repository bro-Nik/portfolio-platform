import React, { useState, useEffect } from 'react';
import { Popover, Checkbox, Space, Button, message } from 'antd';
import { Tag } from 'lucide-react';
import { tagApi } from '../api/tagApi';

const TagAssignPopover = ({ entityType, entityId, assignedTags = [], onUpdate }) => {
  const [open, setOpen] = useState(false);
  const [allTags, setAllTags] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      loadTags();
    }
  }, [open]);

  const loadTags = async () => {
    try {
      const data = await tagApi.getTags();
      setAllTags(data);
      setSelectedIds(new Set(data.filter(t => assignedTags.some(at => at.id === t.id)).map(t => t.id)));
    } catch (error) {
      console.warn('Ошибка загрузки тегов:', error);
    }
  };

  const handleToggle = async (tagId, checked) => {
    setLoading(true);
    const prev = new Set(selectedIds);
    const newSet = new Set(selectedIds);
    if (checked) {
      newSet.add(tagId);
    } else {
      newSet.delete(tagId);
    }
    setSelectedIds(newSet);

    try {
      if (checked) {
        await tagApi.attachTag(tagId, entityType, entityId);
      } else {
        await tagApi.detachTag(tagId, entityType, entityId);
      }
      onUpdate?.();
    } catch (error) {
      setSelectedIds(prev);
      message.error(error.message);
    }
    setLoading(false);
  };

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
      trigger="click"
      title="Назначить теги"
      content={
        <div style={{ minWidth: 200 }}>
          {allTags.length === 0 && <div style={{ color: 'rgba(0,0,0,0.45)', fontSize: '12px' }}>Нет тегов</div>}
          <Checkbox.Group value={[...selectedIds]}>
            <Space direction="vertical" size="small">
              {allTags.map(tag => (
                <Checkbox
                  key={tag.id}
                  value={tag.id}
                  onChange={e => handleToggle(tag.id, e.target.checked)}
                  disabled={loading}
                >
                  <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: '50%', backgroundColor: tag.color || '#1890ff', marginRight: 6 }} />
                  {tag.name}
                </Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </div>
      }
    >
      <Button type="text" size="small" icon={<Tag size={14} />} />
    </Popover>
  );
};

export default TagAssignPopover;
