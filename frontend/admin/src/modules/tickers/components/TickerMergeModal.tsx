import React from 'react';
import { Alert } from '@portfolio/shared';
import { Form, Input, Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useTickerActions } from '../hooks/useTickerActions';

export const TickerMergeModal: React.FC = () => {
  const [form] = Form.useForm();
  const { closeModal } = useModalStore();
  const { mergeTickers, isMerging } = useTickerActions();

  const handleOk = async () => {
    const values = await form.validateFields();
    mergeTickers(Number(values.sourceId), Number(values.targetId));
    closeModal();
  };

  return (
    <Modal
      title="Слияние тикеров"
      open
      onOk={handleOk}
      onCancel={closeModal}
      destroyOnHidden
      confirmLoading={isMerging}
      okText="Объединить"
    >
      <Alert
        title="Тикер-источник будет удалён. Все ссылки (портфели, кошельки, транзакции, external_id, identifiers) будут перенесены на тикер-получатель."
        type="info"
        style={{ marginBottom: 16 }}
      />
      <Form form={form} layout="vertical">
        <Form.Item
          name="sourceId"
          label="ID тикера-источника (будет удалён)"
          rules={[{ required: true, message: 'Введите ID' }]}
        >
          <Input type="number" placeholder="Например: 42" />
        </Form.Item>
        <Form.Item
          name="targetId"
          label="ID тикера-получателя (останется)"
          rules={[{ required: true, message: 'Введите ID' }]}
        >
          <Input type="number" placeholder="Например: 7" />
        </Form.Item>
      </Form>
    </Modal>
  );
};
