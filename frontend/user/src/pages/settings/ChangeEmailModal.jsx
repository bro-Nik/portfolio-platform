import React, { useState } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { authService } from '@portfolio/shared';

const ChangeEmailModal = ({ open, onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { changeEmail } = authService();

  const handleSubmit = async (values) => {
    setLoading(true);
    const result = await changeEmail(values.password, values.newEmail);
    setLoading(false);
    if (result.success) {
      message.success('Письмо с подтверждением отправлено на новый адрес');
      form.resetFields();
      onClose();
    } else {
      message.error(result.error || 'Ошибка смены email');
    }
  };

  return (
    <Modal
      title="Смена email"
      open={open}
      onCancel={onClose}
      footer={null}
      width={500}
      destroyOnClose
      centered
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 16 }}>
        <Form.Item
          name="newEmail"
          label="Новый email"
          rules={[
            { required: true, message: 'Введите новый email' },
            { type: 'email', message: 'Некорректный email' },
          ]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="password"
          label="Текущий пароль"
          rules={[{ required: true, message: 'Введите пароль для подтверждения' }]}
        >
          <Input.Password />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          Сменить email
        </Button>
      </Form>
    </Modal>
  );
};

export default ChangeEmailModal;
