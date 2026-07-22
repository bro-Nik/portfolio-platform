import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useUserActions } from '../hooks/useUserActions';
import { User } from '../../../types/user';

interface UserDelModalProps { user: User }

export const UserDelModal: React.FC<UserDelModalProps> = ({ user }) => {
  const { closeModal } = useModalStore();
  const { deleteUser, isDeleting } = useUserActions();

  if (!user) return null;

  const handleConfirm = async () => {
    deleteUser(user.id);
    closeModal();
  };

  return (
    <Modal
      title="Удалить пользователя?"
      open={true}
      onOk={handleConfirm}
      onCancel={closeModal}
      okText="Удалить"
      cancelText="Отмена"
      okType="danger"
      confirmLoading={isDeleting}
    >
      <p>Вы уверены, что хотите удалить <strong>{user.email}</strong>?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};
