import { useState } from 'react';
import { Button, Input, Popover } from 'antd';
import { MessageSquare } from 'lucide-react';
import { useNotifications } from '@portfolio/shared';

const { TextArea } = Input;

const mutedStyle = { color: 'var(--text-muted)' };

const CommentCell = ({ comment, onSave }) => {
  const { error } = useNotifications();
  const hasComment = Boolean(comment);
  const editable = Boolean(onSave);
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState(comment || '');
  const [saving, setSaving] = useState(false);

  const handleOpenChange = (nextOpen) => {
    if (saving) return;
    if (nextOpen) setValue(comment || '');
    setOpen(nextOpen);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(value.trim());
      setOpen(false);
    } catch (e) {
      error(e.message || 'Не удалось сохранить комментарий');
    } finally {
      setSaving(false);
    }
  };

  const trigger = (
    <span
      className={editable && !hasComment ? 'comment-add' : undefined}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        cursor: editable ? 'pointer' : 'default',
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <MessageSquare size={14} style={{ ...mutedStyle, flexShrink: 0 }} />
    </span>
  );

  if (!editable) {
    return trigger;
  }

  return (
    <Popover
      open={open}
      onOpenChange={handleOpenChange}
      trigger="click"
      placement="bottomLeft"
      destroyOnHidden
      title="Комментарий"
      content={(
        <div style={{ width: 440 }} onClick={(e) => e.stopPropagation()}>
          <TextArea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            rows={9}
            maxLength={500}
            showCount
            variant="filled"
            autoFocus
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 24 }}>
            <Button size="small" onClick={() => setOpen(false)}>Отмена</Button>
            <Button size="small" type="primary" loading={saving} onClick={handleSave}>Сохранить</Button>
          </div>
        </div>
      )}
    >
      {trigger}
    </Popover>
  );
};

export default CommentCell;
