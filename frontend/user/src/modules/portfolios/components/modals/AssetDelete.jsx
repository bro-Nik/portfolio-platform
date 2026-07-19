import React from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { usePortfolioOperations } from 'src/modules/portfolios/hooks/usePortfolioOperations';
import { successToast, errorToast } from 'src/utils/notifications';

const AssetDeleteModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { portfolio, asset } = modalProps;
  const { deleteAsset, loading } = usePortfolioOperations();

  const handleSubmit = async () => {
    const result = await deleteAsset(portfolio, asset);

    if (result.success) {
      successToast('Актив удален');
    } else {
      errorToast(result.error);
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
      <p>Вы уверены, что хотите удалить актив "{asset.name}"?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};

export default AssetDeleteModal;
