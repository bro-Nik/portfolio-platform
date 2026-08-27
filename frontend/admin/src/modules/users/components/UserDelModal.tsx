import { ConfirmDeleteModal, useModalStore } from '@portfolio/shared';
import { useUserActions } from '../hooks/useUserActions';
import { User } from '../../../types/user';

interface UserDelModalProps { user: User }

export const UserDelModal: React.FC<UserDelModalProps> = ({ user }) => {
  const { closeModal } = useModalStore();
  const { deleteUser } = useUserActions();

  if (!user) return null;

  return (
    <ConfirmDeleteModal
      title="Удалить пользователя?"
      entityName={<strong>{user.email}</strong>}
      onConfirm={async () => {
        try {
          await deleteUser(user.id);
          return { success: true };
        } catch (e) {
          return { success: false, error: e instanceof Error ? e.message : undefined };
        }
      }}
      onCancel={closeModal}
    />
  );
};
