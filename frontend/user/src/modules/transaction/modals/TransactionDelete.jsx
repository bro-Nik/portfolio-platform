import React from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useTransactionOperations } from 'src/modules/transaction/hooks/useTransactionOperations';
import { useNotifications } from '@portfolio/shared';

const TransactionDeleteModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { transaction } = modalProps;
  const { deleteTransaction, loading } = useTransactionOperations();

  const handleSubmit = async () => {
    const result = await deleteTransaction(transaction);

    if (result.success) {
      success('Транзакция удалена');
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
      <p>Вы уверены, что хотите удалить транзакцию?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};

export default TransactionDeleteModal;
