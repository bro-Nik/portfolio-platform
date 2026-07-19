import React from 'react';
import { Modal, Form, Input, Button } from 'antd';
import { successToast, errorToast } from 'src/utils/notifications';
import { useAuthMutations } from 'src/hooks/useAuthMutations';

const ChangeEmailModal = ({ open, onClose }) => {
  const [form] = Form.useForm();
  const { changeEmail } = useAuthMutations();

  const handleSubmit = async (values) => {
    const result = await changeEmail.mutateAsync(values);
    if (result.success) {
      successToast('Письмо с подтверждением отправлено на новый адрес');
      form.resetFields();
      onClose();
    } else {
      errorToast(result.error || 'Ошибка смены email');
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
        <Button type="primary" htmlType="submit" loading={changeEmail.isPending} block>
          Сменить email
        </Button>
      </Form>
    </Modal>
  );
};

export default ChangeEmailModal;
