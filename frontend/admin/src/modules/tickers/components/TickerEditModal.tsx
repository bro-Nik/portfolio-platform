import React, { useEffect } from 'react';
import { Form, Input, Modal, Switch } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useTickerActions } from '../hooks/useTickerActions';
import { Ticker } from '../../../types/ticker';

interface TickerEditModalProps { ticker: Ticker }

export const TickerEditModal: React.FC<TickerEditModalProps> = ({ ticker }) => {
  const [form] = Form.useForm();
  const { closeModal } = useModalStore();
  const { updateTicker, isUpdating } = useTickerActions();

  useEffect(() => {
    form.setFieldsValue({
      name: ticker.name,
      symbol: ticker.symbol,
      isActive: ticker.isActive,
    });
  }, [ticker, form]);

  const handleOk = async () => {
    const values = await form.validateFields();
    updateTicker(ticker.id, values);
    closeModal();
  };

  return (
    <Modal
      title={`Редактировать: ${ticker.name}`}
      open
      onOk={handleOk}
      onCancel={closeModal}
      destroyOnHidden
      confirmLoading={isUpdating}
    >
      <Form form={form} layout="vertical">
        <Form.Item name="name" label="Название" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="symbol" label="Символ" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="isActive" label="Активен" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  );
};
