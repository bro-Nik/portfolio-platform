import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { Popover, Input, Button, Space, Tag as AntTag } from 'antd';
import { Tag, Plus, MoreVertical, Trash2 } from 'lucide-react';
import { useTagsQuery } from '../hooks/useTagsQuery';
import { useTagMutations } from '../hooks/useTagMutations';
import { getTagScope } from '../utils/tagScope';
import { useNotifications } from '@portfolio/shared';

const PRESET_COLORS = [
  '#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1',
  '#13c2c2', '#eb2f96', '#fa8c16', '#2f54eb', '#a0d911',
];

const TagForm = ({ initialName, initialColor, onSave, saveLabel, onDelete, onCancel }) => {
  const { error } = useNotifications();
  const [name, setName] = useState(initialName || '');
  const [color, setColor] = useState(initialColor || PRESET_COLORS[0]);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await onSave({ name: name.trim(), color });
      onCancel();
    } catch (err) {
      error(err?.message || 'Ошибка');
    }
    setLoading(false);
  };

  return (
    <div style={{ width: 220, display: 'flex', flexDirection: 'column', gap: 10 }} onMouseDown={e => e.stopPropagation()} onClick={e => e.stopPropagation()}>
      <Input value={name} onChange={e => setName(e.target.value)} placeholder="Название тега" variant="filled" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
        {PRESET_COLORS.map(c => (
          <div key={c} onClick={() => setColor(c)} style={{
            width: 20, height: 20, borderRadius: '50%', cursor: 'pointer', backgroundColor: c,
            border: color === c ? '2px solid #000' : '1px solid #d9d9d9',
          }} />
        ))}
      </div>
      <Space>
        <Button type="primary" size="small" loading={loading} onClick={handleSave}>{saveLabel}</Button>
        <Button size="small" onClick={onCancel}>Отмена</Button>
        {onDelete && <Button type="text" size="small" danger icon={<Trash2 size={14} />} loading={loading} onClick={onDelete} />}
      </Space>
    </div>
  );
};

const TagRow = ({ tag, entityType, onToggle }) => {
  const [editOpen, setEditOpen] = useState(false);
  const { success } = useNotifications();
  const { updateTag, deleteTag } = useTagMutations();

  const handleSave = async ({ name, color }) => {
    await updateTag.mutateAsync({ tagId: tag.id, data: { name, color } });
    success('Тег обновлён');
  };

  const handleDelete = async () => {
    await deleteTag.mutateAsync(tag.id);
    success('Тег удалён');
    setEditOpen(false);
  };

  const handleClick = (e) => {
    if (!entityType || !onToggle) return;
    e.stopPropagation();
    onToggle(tag.id);
  };

  const tagColor = tag.color || '#1890ff';
  const canToggle = entityType && onToggle;

  return (
    <div className="tag-row" onClick={canToggle ? handleClick : undefined}
      style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '3px 6px', borderRadius: 4, cursor: canToggle ? 'pointer' : 'default' }}>
      <AntTag color={tagColor} style={{ margin: 0, fontSize: 12, lineHeight: '18px' }}>
        {tag.name}
      </AntTag>

      <div style={{ flex: 1 }} />

      <Popover
        open={editOpen}
        onOpenChange={setEditOpen}
        content={<TagForm initialName={tag.name} initialColor={tag.color} onSave={handleSave} saveLabel="Сохранить" onDelete={handleDelete} onCancel={() => setEditOpen(false)} />}
        trigger="click" arrow={false}
        placement="left"
      >
        <Button
          type="text"
          size="small"
          className={`tag-row-actions${editOpen ? ' visible' : ''}`}
          icon={<MoreVertical size={14} />}
          style={{ flexShrink: 0 }}
          onClick={e => e.stopPropagation()}
        />
      </Popover>
    </div>
  );
};

const TagPanel = ({ entityType, entityId, assignedTags, parentId }) => {
  const { success, error } = useNotifications();
  const scope = getTagScope(entityType);
  const { data: allTags = [] } = useTagsQuery();
  const { createTag, attachTag, detachTag } = useTagMutations();
  const [search, setSearch] = useState('');
  const [createOpen, setCreateOpen] = useState(false);

  const [selectedIds, setSelectedIds] = useState(() => new Set());
  const selectedIdsRef = useRef(selectedIds);

  useEffect(() => { selectedIdsRef.current = selectedIds; }, [selectedIds]);

  const [prevAssignedTags, setPrevAssignedTags] = useState(assignedTags);
  if (prevAssignedTags !== assignedTags) {
    setPrevAssignedTags(assignedTags);
    if (assignedTags) setSelectedIds(new Set(assignedTags.map(t => t.id)));
  }

  const handleToggle = useCallback(async (tagId) => {
    const current = selectedIdsRef.current;
    const isChecked = current.has(tagId);
    const prev = new Set(current);
    const next = new Set(current);
    if (isChecked) next.delete(tagId); else next.add(tagId);
    setSelectedIds(next);

    const mutation = isChecked ? detachTag : attachTag;
    try {
      await mutation.mutateAsync({ tagId, entityType, entityId, parentId });
    } catch (err) {
      setSelectedIds(prev);
      error(err?.message || 'Произошла ошибка');
    }
  }, [attachTag, detachTag, entityType, entityId, parentId, error]);

  const handleCreate = async ({ name, color }) => {
    await createTag.mutateAsync({ name, color, scope });
    success('Тег создан');
  };

  const filtered = useMemo(() => {
    const scoped = scope ? allTags.filter(t => t.scope === scope) : allTags;
    if (!search) return scoped;
    return scoped.filter(t => t.name.toLowerCase().includes(search.toLowerCase()));
  }, [allTags, scope, search]);

  const selected = useMemo(() => {
    if (!entityType) return [];
    return filtered.filter(t => selectedIds.has(t.id));
  }, [filtered, selectedIds, entityType]);

  const unselected = useMemo(() => {
    if (!entityType) return filtered;
    return filtered.filter(t => !selectedIds.has(t.id));
  }, [filtered, selectedIds, entityType]);

  const hasItems = selected.length > 0 || unselected.length > 0;

  return (
    <div style={{ width: 260, maxHeight: 400 }} onClick={e => e.stopPropagation()}>
      <style>{`.tag-row-actions { opacity: 0; } .tag-row:hover { background-color: var(--ant-table-row-hover-bg, rgba(0,0,0,0.04)); } .tag-row:hover .tag-row-actions, .tag-row-actions.visible { opacity: 1; }`}</style>
      <Input
        placeholder="Поиск..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        allowClear
        variant="filled"
        style={{ marginBottom: 8 }}
        onClick={e => e.stopPropagation()}
      />

      <div style={{ maxHeight: 260, overflowY: 'auto' }}>
        {!hasItems && (
          <div style={{ color: 'var(--text-muted)', fontSize: 12, textAlign: 'center', padding: '12px 0' }}>
            Теги не найдены
          </div>
        )}

        {selected.length > 0 && (
          <>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', padding: '2px 6px', marginBottom: 2 }}>
              Выбранные
            </div>
            {selected.map(tag => (
              <TagRow key={tag.id} tag={tag} checked={true} entityType={entityType} onToggle={handleToggle} />
            ))}
          </>
        )}

        {(selected.length > 0 && unselected.length > 0) && (
          <div style={{ fontSize: 11, color: 'var(--text-muted)', padding: '2px 6px', marginTop: 6, marginBottom: 2 }}>
            Все теги
          </div>
        )}

        {(selected.length > 0 ? unselected : filtered).map(tag => (
          <TagRow
            key={tag.id}
            tag={tag}
            checked={selectedIds.has(tag.id)}
            entityType={entityType}
            onToggle={handleToggle}
          />
        ))}
      </div>

      <Popover
        open={createOpen}
        onOpenChange={setCreateOpen}
        trigger="click" arrow={false}
        placement="top"
        content={<TagForm onSave={handleCreate} saveLabel="Создать" onCancel={() => setCreateOpen(false)} />}
      >
        <Button type="dashed" block size="small" icon={<Plus size={14} />} style={{ marginTop: 8 }} onClick={e => e.stopPropagation()}>
          Создать тег
        </Button>
      </Popover>
    </div>
  );
};

const TagManagerSelect = ({ trigger = 'menu', entityType, entityId, assignedTags = [], parentId, children }) => {
  const [open, setOpen] = useState(false);

  if (trigger === 'inline') {
    return (
      <Popover
        open={open}
        onOpenChange={setOpen}
        trigger="click" arrow={false}
        placement="bottom"
        content={<TagPanel entityType={entityType} entityId={entityId} assignedTags={assignedTags} parentId={parentId} />}
      >
        <span onClick={e => e.stopPropagation()} style={{ display: 'inline-block' }}>
          {children}
        </span>
      </Popover>
    );
  }

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
      trigger="click" arrow={false}
      placement="rightTop"
      content={<TagPanel entityType={entityType} entityId={entityId} assignedTags={assignedTags} parentId={parentId} />}
    >
      <div onClick={e => e.stopPropagation()} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
        <Tag size={16} />
        <span>Теги</span>
      </div>
    </Popover>
  );
};

export { TagManagerSelect, TagPanel };
export default TagManagerSelect;
