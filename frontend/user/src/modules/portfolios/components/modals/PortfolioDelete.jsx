import React from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { usePortfolioOperations } from '../../hooks/usePortfolioOperations';
import { successToast, errorToast } from 'src/utils/notifications';

const PortfolioDeleteModal = () => {
  const { modalProps, closeModal } = useModalStore();
  const { portfolio } = modalProps;
  const { deletePortfolio, loading } = usePortfolioOperations();

  const handleSubmit = async () => {
    const result = await deletePortfolio(portfolio);

    if (result.success) {
      successToast('Портфель удален');
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
      <p>Вы уверены, что хотите удалить портфель "{portfolio.name}"?</p>
      <p style={{ color: '#ff4d4f', fontSize: '12px' }}>
        Это действие нельзя отменить.
      </p>
    </Modal>
  );
};

export default PortfolioDeleteModal;
