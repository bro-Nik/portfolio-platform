import React from 'react';
import { Modal, message } from 'antd';
import { useModalStore } from '/app/src/stores/modalStore';
import { useWalletOperations } from '../../hooks/useWalletOperations';

const WalletDeleteModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { wallet } = modalProps;
  const { deleteWallet, loading } = useWalletOperations();

  const handleSubmit = async () => {
    const result = await deleteWallet(wallet);

    if (result.success) {
      message.success('Кошелек удален');
    } else {
      message.error(result.error);
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
      centered
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
