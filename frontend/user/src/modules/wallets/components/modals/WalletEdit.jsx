import React, { useEffect } from 'react';
import { Modal, Form, Input, Button, Space } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useWalletOperations } from '../../hooks/useWalletOperations';
import ShowMore from 'src/components/ui/ShowMore';
import FormComment from 'src/features/forms/FormComment';
import FormActionBtns from 'src/features/forms/FormActionBtns';
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
      title={title}
      open={true}
      onCancel={handleCancel}
      footer={null}
      width={500}
      destroyOnHidden
    >
      <Form
        form={form}
        onFinish={handleSubmit}
        requiredMark="optional"
        size="middle"
      >
        <Space orientation="vertical" style={{ width: '100%' }} size="middle">
          {/* Основные поля */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Form.Item
              label="Название"
              name="name"
              rules={[
                { required: true, message: 'Введите название кошелька' },
                { min: 2, message: 'Минимум 2 символа' },
                { max: 50, message: 'Максимум 50 символов' }
              ]}
            >
              <Input 
                placeholder="Мой кошелек" 
                autoFocus
              />
            </Form.Item>
          </div>

          {/* Кнопка "Еще" */}
          <ShowMore content={<FormComment />} show={!!wallet?.comment}/>

          {/* Кнопки действий */}
          <FormActionBtns
            title={wallet ? 'Сохранить' : 'Добавить'} 
            onCancel={handleCancel}
            loading={loading}
          />

        </Space>
      </Form>
    </Modal>
  );
};

export default WalletEditModal;
