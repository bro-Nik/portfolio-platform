import React, { useEffect } from 'react';
import { Modal, Form, Input } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useWalletOperations } from '../../hooks/useWalletOperations';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import { useSubview } from 'src/hooks/useSubview';
import { useNotifications } from '@portfolio/shared';

const WalletEditModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { 
    wallet = null,
    title = wallet ? 'Редактировать кошелек' : 'Добавить кошелек'
  } = modalProps;

  const [form] = Form.useForm();
  const { editWallet, loading } = useWalletOperations();
  const { subview, openSubview, closeSubview } = useSubview();

  useEffect(() => {
    form.setFieldsValue({
      name: wallet?.name || '',
      comment: wallet?.comment || ''
    });
  }, [wallet, form]);

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      // Добавляем ID если редактируем
      ...(wallet && { id: wallet.id })
    };

    const result = await editWallet(submitData);
    
    if (result.success) {
      success(wallet ? 'Кошелек обновлен' : 'Кошелек создан');
      closeModal();
    } else {
      error(result.error || 'Произошла ошибка');
      console.log(result.error || 'Произошла ошибка')
    }
  };

  const handleCancel = () => {
    form.resetFields();
    closeModal();
  };

  return (
    <Modal
      title={subview ? null : title}
      open={true}
      onCancel={handleCancel}
      closable={!subview}
      footer={null}
      width={500}
      destroyOnHidden
    >
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
            {/* Основные поля */}
            <Form.Item
              label="Название"
              name="name"
              rules={[
                { required: true, message: 'Введите название кошелька' },
                { min: 2, message: 'Минимум 2 символа' },
                { max: 50, message: 'Максимум 50 символов' }
              ]}
            >
              <Input autoFocus />
            </Form.Item>

            {/* Комментарий */}
            <MetaRowGroup onComment={() => openSubview('comment')} />

            {/* Кнопки действий */}
            <FormActionBtns title="Сохранить" onCancel={handleCancel} loading={loading} />

          </>
        )}
      </Form>
    </Modal>
  );
};

export default WalletEditModal;
