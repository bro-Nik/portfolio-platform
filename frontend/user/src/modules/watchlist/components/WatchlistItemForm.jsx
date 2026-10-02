import React, { useEffect } from 'react';
import { Form } from 'antd';
import { useNotifications } from '@portfolio/shared';
import { useWatchlistOperations } from '../hooks/useWatchlistOperations';
import { useSubview } from 'src/hooks/useSubview';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import FormActionBtns from 'src/features/forms/FormActionBtns';

const WatchlistItemForm = ({ item, onSuccess, onCancel, onSubviewChange }) => {
  const { success, error } = useNotifications();
  const { editItemComment, loading } = useWatchlistOperations();
  const { subview, openSubview, closeSubview } = useSubview();
  const [form] = Form.useForm();

  useEffect(() => {
    onSubviewChange?.(subview);
  }, [subview, onSubviewChange]);

  useEffect(() => {
    form.setFieldsValue({ comment: item?.comment || '' });
  }, [item, form]);

  const handleSubmit = async () => {
    const result = await editItemComment(item.id, form.getFieldValue('comment') || null);
    if (result.success) {
      success('Запись обновлена');
      onSuccess?.();
    } else {
      error(result.error || 'Произошла ошибка');
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel?.();
  };

  return (
    <Form
      form={form}
      onFinish={handleSubmit}
      layout="vertical"
      requiredMark={false}
      size="middle"
    >
      {subview === 'comment' ? (
        <CommentSubview onClose={closeSubview} />
      ) : (
        <>
          <MetaRowGroup onComment={() => openSubview('comment')} />
          <FormActionBtns title="Сохранить" onCancel={handleCancel} loading={loading} />
        </>
      )}
    </Form>
  );
};

export default WatchlistItemForm;
