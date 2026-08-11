import { useEffect } from 'react';
import { Modal, Form, Input, Select, Space, Button } from 'antd';
import { roles, statuses } from '../constants';
import { useModalStore } from '@portfolio/shared';
import { useUserActions } from '../hooks/useUserActions';
import { User, UserFormData } from '../../../types/user';

interface UserFormModalProps { user?: User }

export const UserFormModal: React.FC = () => {
  const { modalProps, closeModal } = useModalStore();
  const { user } = modalProps as UserFormModalProps;
  const { createUser, updateUser, isCreating, isUpdating } = useUserActions();

  const [form] = Form.useForm();
  const editMode = !!user?.id;

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        email: user.email,
        fullName: user.fullName,
        role: user.role,
        status: user.status,
      });
    } else {
      form.resetFields();
    }
  }, [user, form]);

  const handleSubmit = (values: UserFormData) => {
    const data = editMode
      ? values
      : { ...values, password: values.password || undefined };

    if (editMode && user) {
      updateUser(user.id, data);
    } else {
      createUser(data);
    }
    closeModal();
  };

  const handleCancel = () => {
    form.resetFields();
    closeModal();
  };

  return (
    <Modal
      title={editMode ? 'Редактировать пользователя' : 'Создать пользователя'}
      open={true}
      onCancel={handleCancel}
      destroyOnHidden
      footer={null}
      width={600}
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Введите email' },
            { type: 'email', message: 'Введите корректный email' },
          ]}
        >
          <Input placeholder="user@example.com" />
        </Form.Item>

        <Form.Item name="fullName" label="Полное имя">
          <Input placeholder="Иван Иванов" />
        </Form.Item>

        <Form.Item name="role" label="Роль" rules={[{ required: true, message: 'Выберите роль' }]}>
          <Select options={roles} placeholder="Выберите роль" />
        </Form.Item>

        <Form.Item name="status" label="Статус">
          <Select options={statuses} placeholder="Выберите статус" />
        </Form.Item>

        {editMode ? (
          <Form.Item
            name="password"
            label="Новый пароль"
            rules={[{ min: 6, message: 'Минимум 6 символов' }]}
          >
            <Input.Password placeholder="Оставьте пустым, чтобы не менять" />
          </Form.Item>
        ) : (
          <Form.Item
            name="password"
            label="Пароль"
            rules={[{ min: 6, message: 'Минимум 6 символов' }]}
          >
            <Input.Password placeholder="Оставьте пустым для автогенерации" />
          </Form.Item>
        )}

        <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
          <Space>
            <Button onClick={handleCancel}>Отмена</Button>
            <Button type="primary" htmlType="submit" loading={isCreating || isUpdating}>
              {editMode ? 'Сохранить' : 'Создать'}
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
};
