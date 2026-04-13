import { useModalStore } from '@shared';
import { UserDelModal } from '../components/UserDelModal';
import { UserDetailsModal } from '../components/UserDetailsModal';
import { UserFormModal } from '../components/UserFormModal';
import { User } from '/app/src/types/user';

export const useUserModals = () => {
  const { openModal } = useModalStore();

  return {
    userDetailsModal: (user: User) => openModal(UserDetailsModal, { user }),
    userFormModal: (user?: User) => openModal(UserFormModal, { user }),
    userDeleteConfirmModal: (user: User) => openModal(UserDelModal, { user }),
  };
};
