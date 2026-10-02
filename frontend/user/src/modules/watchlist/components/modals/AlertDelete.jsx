import React from 'react';
import { Modal } from 'antd';
import { useModalStore, useNotifications } from '@portfolio/shared';
import { useWatchlistOperations } from '../../hooks/useWatchlistOperations';

const AlertDeleteModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { alert } = modalProps;
  const { deleteAlert, loading } = useWatchlistOperations();

  const handleSubmit = async () => {
    const result = await deleteAlert(alert.id);
    if (result.success) {
      success('Уведомление удалено');
    } else {
      error(result.error);
    }
    closeModal();
  };

  return (
    <Modal
      title="Подтверждение удаления"
      open={true}
      onOk={handleSubmit}
      onCancel={closeModal}
      okText="Удалить"
      cancelText="Отмена"
      okType="danger"
      confirmLoading={loading}
    >
      <p>Вы уверены, что хотите удалить это уведомление?</p>
    </Modal>
  );
};

export default AlertDeleteModal;
