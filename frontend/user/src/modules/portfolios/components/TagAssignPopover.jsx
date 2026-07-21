import React, { useState, useEffect } from 'react';
import { Popover, Checkbox, Space, Button } from 'antd';
import { Tag } from 'lucide-react';
import { useTagsQuery } from '../hooks/useTagsQuery';
import { useTagMutations } from '../hooks/useTagMutations';
import { useNotifications } from '@portfolio/shared';

const TagAssignPopover = ({ entityType, entityId, assignedTags = [], onUpdate }) => {
  const { error } = useNotifications();
  const [open, setOpen] = useState(false);
  const { data: allTags = [] } = useTagsQuery();
  const { attachTag, detachTag } = useTagMutations();
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (allTags.length > 0) {
      setSelectedIds(new Set(allTags.filter(t => assignedTags.some(at => at.id === t.id)).map(t => t.id)));
    }
  }, [allTags, assignedTags]);

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

    const mutation = checked ? attachTag : detachTag;
    try {
      await mutation.mutateAsync({ tagId, entityType, entityId });
      onUpdate?.();
    } catch (error) {
      setSelectedIds(prev);
      error(error?.message || 'Произошла ошибка');
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
          {allTags.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Нет тегов</div>}
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
