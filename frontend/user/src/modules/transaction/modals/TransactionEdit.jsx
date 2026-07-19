import React from 'react';
import { useModalStore } from '@portfolio/shared';
import { Modal } from 'antd';
import BaseTransactionForm from 'src/modules/transaction/components/TransactionEdit/BaseTransactionForm';
import { useTransactionOperations } from 'src/modules/transaction/hooks/useTransactionOperations';
import { successToast, errorToast } from 'src/utils/notifications';

const TransactionEditModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { tickerId = null, portfolioId = null, walletId = null, transaction = null } = modalProps;
  const { editTransaction, loading } = useTransactionOperations();
  const title = transaction?.id ? 'Изменить транзакцию' : 'Добавить транзакцию';

  const onSubmit = async (submitData) => {
    const result = await editTransaction(transaction, submitData);

    if (result.success) {
      successToast(transaction ? 'Транзакция обновлена' : 'Транзакция добавлена');
      closeModal();
    } else {
      errorToast(result.error || 'Произошла ошибка');
    }
  };

  return (
    <Modal
      title={title}
      open={true}
      onCancel={closeModal}
      footer={null}
      width={500}
      destroyOnHidden
      centered
    >
      <BaseTransactionForm
        tickerId={tickerId}
        walletId={walletId}
        portfolioId={portfolioId}
        transaction={transaction}
        onCancel={closeModal}
        onSubmit={onSubmit}
        loading={loading}
      />
    </Modal>
  );
};

export default TransactionEditModal;
