import React, { useEffect } from 'react';
import { Form, Input } from 'antd';
import { useNotifications } from '@portfolio/shared';
import { usePortfolioOperations } from '../hooks/usePortfolioOperations';
import { useSubview } from 'src/hooks/useSubview';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import FormSelect from 'src/features/forms/FormSelect';
import { MARKETS } from 'src/constants/markets';

const PortfolioForm = ({ initialMarket = 'crypto', submitText = 'Сохранить', onSuccess, onCancel, onSubviewChange }) => {
  const { success, error } = useNotifications();
  const { editPortfolio, loading } = usePortfolioOperations();
  const { subview, openSubview, closeSubview } = useSubview();
  const [form] = Form.useForm();

  useEffect(() => {
    onSubviewChange?.(subview);
  }, [subview, onSubviewChange]);

  useEffect(() => {
    form.setFieldsValue({
      name: '',
      market: initialMarket,
      comment: ''
    });
  }, [initialMarket, form]);

  const handleSubmit = async (values) => {
    const result = await editPortfolio(values);

    if (result.success) {
      success('Портфель создан');
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
            options={MARKETS}
            variant="filled"
          />

          <MetaRowGroup onComment={() => openSubview('comment')} />

          <FormActionBtns title={submitText} onCancel={handleCancel} loading={loading} />
        </>
      )}
    </Form>
  );
};

export default PortfolioForm;
