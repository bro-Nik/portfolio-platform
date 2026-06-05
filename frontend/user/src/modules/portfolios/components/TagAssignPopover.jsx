import React, { useState, useEffect } from 'react';
import { Popover, Checkbox, Space, Button, message } from 'antd';
import { TagIcon } from '@heroicons/react/16/solid';
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
    const result = await tagApi.getTags();
    if (result.success) {
      setAllTags(result.data);
      setSelectedIds(new Set(result.data.filter(t => assignedTags.some(at => at.id === t.id)).map(t => t.id)));
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

    const result = checked
      ? await tagApi.attachTag(tagId, entityType, entityId)
      : await tagApi.detachTag(tagId, entityType, entityId);

    if (!result.success) {
      setSelectedIds(prev);
      message.error(result.error);
    } else {
      onUpdate?.();
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
          {allTags.length === 0 && <div className="text-muted small">Нет тегов</div>}
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
      <Button type="text" size="small" icon={<TagIcon width={14} />} />
    </Popover>
  );
};

export default TagAssignPopover;
