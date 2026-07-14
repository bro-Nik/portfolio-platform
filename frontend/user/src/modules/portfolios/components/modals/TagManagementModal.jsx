import React, { useState, useEffect } from 'react';
import { Modal, Input, Button, Space, message } from 'antd';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { useModalStore } from '/app/src/stores/modalStore';
import { tagApi } from '../../api/tagApi';

const PRESET_COLORS = [
  '#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1',
  '#13c2c2', '#eb2f96', '#fa8c16', '#2f54eb', '#a0d911',
];

const TagManagementModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { onTagsChange } = modalProps;

  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState('');
  const [editColor, setEditColor] = useState(PRESET_COLORS[0]);
  const [showForm, setShowForm] = useState(false);

  const loadTags = async () => {
    const result = await tagApi.getTags();
    if (result.success) {
      setTags(result.data);
    }
  };

  useEffect(() => {
    loadTags();
  }, []);

  const handleCreate = async () => {
    if (!editName.trim()) return;
    setLoading(true);
    const result = await tagApi.createTag(editName.trim(), editColor);
    if (result.success) {
      message.success('Тег создан');
      setEditName('');
      setShowForm(false);
      await loadTags();
      onTagsChange?.();
    } else {
      message.error(result.error);
    }
    setLoading(false);
  };

  const handleUpdate = async () => {
    if (!editName.trim()) return;
    setLoading(true);
    const result = await tagApi.updateTag(editId, { name: editName.trim(), color: editColor });
    if (result.success) {
      message.success('Тег обновлён');
      setEditId(null);
      setEditName('');
      setShowForm(false);
      await loadTags();
      onTagsChange?.();
    } else {
      message.error(result.error);
    }
    setLoading(false);
  };

  const handleDelete = async (tagId) => {
    setLoading(true);
    const result = await tagApi.deleteTag(tagId);
    if (result.success) {
      message.success('Тег удалён');
      await loadTags();
      onTagsChange?.();
    } else {
      message.error(result.error);
    }
    setLoading(false);
  };

  const startEdit = (tag) => {
    setEditId(tag.id);
    setEditName(tag.name);
    setEditColor(tag.color || PRESET_COLORS[0]);
    setShowForm(true);
  };

  return (
    <Modal title="Управление тегами" open={true} onCancel={closeModal} footer={null} width={500} destroyOnClose centered>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {tags.map(tag => (
          <div key={tag.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ display: 'inline-block', width: 12, height: 12, borderRadius: '50%', backgroundColor: tag.color || '#1890ff' }} />
            <span style={{ flex: 1 }}>{tag.name}</span>
            <Button type="text" size="small" icon={<Pencil size={14} />} onClick={() => startEdit(tag)} />
            <Button type="text" size="small" danger icon={<Trash2 size={14} />} onClick={() => handleDelete(tag.id)} />
          </div>
        ))}

        {showForm && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 12, border: '1px solid #d9d9d9', borderRadius: 6 }}>
            <Input value={editName} onChange={e => setEditName(e.target.value)} placeholder="Название тега" />
            <Space size="small">
              {PRESET_COLORS.map(c => (
                <div key={c} onClick={() => setEditColor(c)} style={{
                  width: 20, height: 20, borderRadius: '50%', cursor: 'pointer', backgroundColor: c,
                  border: editColor === c ? '2px solid #000' : '1px solid #d9d9d9',
                }} />
              ))}
            </Space>
            <Space>
              <Button type="primary" size="small" loading={loading} onClick={editId ? handleUpdate : handleCreate}>
                {editId ? 'Сохранить' : 'Создать'}
              </Button>
              <Button size="small" onClick={() => { setShowForm(false); setEditId(null); setEditName(''); }}>
                Отмена
              </Button>
            </Space>
          </div>
        )}

        {!showForm && (
          <Button type="dashed" block icon={<Plus size={14} />} onClick={() => { setShowForm(true); setEditId(null); setEditName(''); }}>
            Создать тег
          </Button>
        )}
      </Space>
    </Modal>
  );
};

export default TagManagementModal;
