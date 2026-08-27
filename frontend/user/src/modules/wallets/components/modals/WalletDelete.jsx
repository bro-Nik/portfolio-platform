import { ConfirmDeleteModal, useModalStore } from '@portfolio/shared';
import { useWalletOperations } from '../../hooks/useWalletOperations';

const WalletDeleteModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { wallet } = modalProps;
  const { deleteWallet } = useWalletOperations();

  return (
    <ConfirmDeleteModal
      entityName={wallet.name}
      successMessage="Кошелек удален"
      onConfirm={() => deleteWallet(wallet)}
      onCancel={closeModal}
    />
  );
};

export default WalletDeleteModal;
