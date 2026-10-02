import React from 'react';
import { Modal } from 'antd';
import { useModalStore, useNotifications } from '@portfolio/shared';
import { useWatchlistOperations } from '../../hooks/useWatchlistOperations';

const WatchlistAssetDeleteModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { item } = modalProps;
  const { deleteItem, loading } = useWatchlistOperations();

  const handleSubmit = async () => {
    const result = await deleteItem(item.id);
    if (result.success) {
      success('Актив удалён из избранного');
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
      <p>Убрать &quot;{item?.name || item?.symbol}&quot; из избранного?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Все уведомления по этому активу тоже будут удалены.
      </p>
    </Modal>
  );
};

export default WatchlistAssetDeleteModal;
