import React from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useWalletOperations } from '../../hooks/useWalletOperations';
import { useNotifications } from '@portfolio/shared';

const WalletDeleteModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { wallet } = modalProps;
  const { deleteWallet, loading } = useWalletOperations();

  const handleSubmit = async () => {
    const result = await deleteWallet(wallet);

    if (result.success) {
      success('Кошелек удален');
    } else {
      error(result.error);
    }
    closeModal();
  };

  const handleCancel = () => {
    closeModal();
  };

  return (
    <Modal
      title="Подтверждение удаления"
      open={true}
      onOk={handleSubmit}
      onCancel={handleCancel}
      okText="Удалить"
      cancelText="Отмена"
      okType="danger"
      confirmLoading={loading}
    >
      <p>Вы уверены, что хотите удалить кошелек "{wallet.name}"?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};

export default WalletDeleteModal;
