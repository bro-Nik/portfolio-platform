import React, { useEffect } from 'react';
import { Form, Input } from 'antd';
import { useNotifications } from '@portfolio/shared';
import { useWalletOperations } from '../hooks/useWalletOperations';
import { useSubview } from 'src/hooks/useSubview';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import FormActionBtns from 'src/features/forms/FormActionBtns';

const WalletForm = ({ wallet = null, submitText = 'Сохранить', onSuccess, onCancel, onSubviewChange }) => {
  const { success, error } = useNotifications();
  const { editWallet, loading } = useWalletOperations();
  const { subview, openSubview, closeSubview } = useSubview();
  const [form] = Form.useForm();

  useEffect(() => {
    onSubviewChange?.(subview);
  }, [subview, onSubviewChange]);

  useEffect(() => {
    form.setFieldsValue({
      name: wallet?.name || '',
      comment: wallet?.comment || ''
    });
  }, [wallet, form]);

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      comment: form.getFieldValue('comment'),
      ...(wallet && { id: wallet.id })
    };

    const result = await editWallet(submitData);

    if (result.success) {
      success(wallet ? 'Кошелек обновлен' : 'Кошелек создан');
      onSuccess?.(result.data);
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
      requiredMark="optional"
      size="middle"
    >
      {subview === 'comment' ? (
        <CommentSubview onClose={closeSubview} />
      ) : (
        <>
          <Form.Item
            label="Название"
            name="name"
            rules={[
              { required: true, message: 'Введите название кошелька' },
              { min: 2, message: 'Минимум 2 символа' },
              { max: 50, message: 'Максимум 50 символов' }
            ]}
          >
            <Input autoFocus variant="filled" />
          </Form.Item>

          <MetaRowGroup onComment={() => openSubview('comment')} />

          <FormActionBtns title={submitText} onCancel={handleCancel} loading={loading} />
        </>
      )}
    </Form>
  );
};

export default WalletForm;
