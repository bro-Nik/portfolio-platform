import React, { useState } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { authService } from '@portfolio/shared';

const ChangePasswordModal = ({ open, onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { changePassword } = authService();

  const handleSubmit = async (values) => {
    setLoading(true);
    const result = await changePassword(values.currentPassword, values.newPassword);
    setLoading(false);
    if (result.success) {
      message.success('Пароль успешно изменён');
      form.resetFields();
      onClose();
    } else {
      message.error(result.error || 'Ошибка смены пароля');
    }
  };

  return (
    <Modal
      title="Смена пароля"
      open={open}
      onCancel={onClose}
      footer={null}
      width={500}
      destroyOnClose
      centered
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 16 }}>
        <Form.Item
          name="currentPassword"
          label="Текущий пароль"
          rules={[{ required: true, message: 'Введите текущий пароль' }]}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item
          name="newPassword"
          label="Новый пароль"
          rules={[
            { required: true, message: 'Введите новый пароль' },
            { min: 8, message: 'Минимум 8 символов' },
          ]}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item
          name="confirmPassword"
          label="Подтвердите пароль"
          dependencies={['newPassword']}
          rules={[
            { required: true, message: 'Подтвердите новый пароль' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('newPassword') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('Пароли не совпадают'));
              },
            }),
          ]}
        >
          <Input.Password />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          Сменить пароль
        </Button>
      </Form>
    </Modal>
  );
};

export default ChangePasswordModal;
