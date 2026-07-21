import React from 'react';
import { Modal, Form, Input, Button, Typography } from 'antd';
import { AlertTriangle } from 'lucide-react';
import { useAuthStore } from '@portfolio/shared';
import { useNavigate } from 'react-router-dom';
import { useNotifications } from '@portfolio/shared';
import { useAuthMutations } from 'src/hooks/useAuthMutations';

const { Text } = Typography;

const DeleteAccountModal = ({ open, onClose }) => {
  const { success, error } = useNotifications();
  const [form] = Form.useForm();
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const { deleteAccount } = useAuthMutations();

  const handleSubmit = async (values) => {
    const result = await deleteAccount.mutateAsync(values.currentPassword);
    if (result.success) {
      success('Аккаунт успешно удалён');
      logout();
      navigate('/');
    } else {
      error(result.error || 'Ошибка удаления аккаунта');
    }
  };

  return (
    <Modal
      title="Удаление аккаунта"
      open={open}
      onCancel={onClose}
      footer={null}
      width={500}
      destroyOnClose
      centered
    >
      <div style={{ marginTop: 8, marginBottom: 20 }}>
        <div style={{
          display: 'flex',
          gap: 10,
          padding: 12,
          background: '#fff1f0',
          borderRadius: 8,
          border: '1px solid #ffa39e',
          marginBottom: 16,
        }}>
          <AlertTriangle size={18} style={{ color: '#f5222d', flexShrink: 0, marginTop: 2 }} />
          <div>
            <Text style={{ color: '#cf1322', fontWeight: 600, fontSize: 14 }}>
              Это действие нельзя отменить.
            </Text>
            <br />
            <Text style={{ color: '#820014', fontSize: 13 }}>
              Все ваши данные, включая портфели, кошельки и транзакции, будут безвозвратно удалены.
            </Text>
          </div>
        </div>

        <Text style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          Введите текущий пароль для подтверждения удаления аккаунта.
        </Text>
      </div>

      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item
          name="currentPassword"
          label="Текущий пароль"
          rules={[{ required: true, message: 'Введите текущий пароль' }]}
        >
          <Input.Password />
        </Form.Item>
        <Button
          danger
          type="primary"
          htmlType="submit"
          loading={deleteAccount.isPending}
          block
        >
          Удалить аккаунт
        </Button>
      </Form>
    </Modal>
  );
};

export default DeleteAccountModal;
