import React, { useEffect } from 'react';
import { Modal, Form, Input } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { usePortfolioOperations } from '../../hooks/usePortfolioOperations';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import FormSelect from 'src/features/forms/FormSelect';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import { useSubview } from 'src/hooks/useSubview';
import { useNotifications } from '@portfolio/shared';

const PortfolioEditModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { 
    portfolio = null,
    title = portfolio ? 'Редактировать портфель' : 'Добавить портфель'
  } = modalProps;

  const [form] = Form.useForm();
  const { editPortfolio, loading } = usePortfolioOperations();
  const { subview, openSubview, closeSubview } = useSubview();

  useEffect(() => {
    form.setFieldsValue({
      name: portfolio?.name || '',
      market: portfolio?.market || 'crypto',
      comment: portfolio?.comment || ''
    });
  }, [portfolio, form]);

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      // Добавляем ID если редактируем
      ...(portfolio && { id: portfolio.id })
    };

    const result = await editPortfolio(submitData);

    if (result.success) {
      success(portfolio ? 'Портфель обновлен' : 'Портфель создан');
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

  const markets = [
    {value: 'crypto', label: 'Крипто'},
    {value: 'stocks', label: 'Акции'},
    {value: 'currency', label: 'Валюта'},
  ];

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
        requiredMark={false}
        size="middle"
      >
        {subview === 'comment' ? (
          <CommentSubview onClose={closeSubview} />
        ) : (
          <>
            {/* Основные поля */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <Form.Item
                label="Название"
                name="name"
                rules={[
                  { required: true, message: 'Введите название портфеля' },
                  { min: 2, message: 'Минимум 2 символа' },
                  { max: 50, message: 'Максимум 50 символов' }
                ]}
              >
                <Input autoFocus variant="filled" />
              </Form.Item>

              <FormSelect
                name="market"
                label="Рынок"
                rules={[{ required: true, message: 'Выберите рынок' }]}
                options={markets}
                disabled={!!portfolio && portfolio.assets?.length > 0}
                variant="filled"
              />
            </div>

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

export default PortfolioEditModal;
