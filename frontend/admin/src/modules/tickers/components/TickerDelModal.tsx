import React from 'react';
import { Modal } from 'antd';
import { useModalStore } from '@portfolio/shared';
import { useTickerActions } from '../hooks/useTickerActions';
import { Ticker } from '../../../types/ticker';

interface TickerDelModalProps { ticker: Ticker }

export const TickerDelModal: React.FC<TickerDelModalProps> = ({ ticker }) => {
  const { closeModal } = useModalStore();
  const { deleteTicker, isDeleting } = useTickerActions();

  const handleConfirm = () => {
    deleteTicker(ticker.id);
    closeModal();
  };

  return (
    <Modal
      title="Удаление тикера"
      open
      onOk={handleConfirm}
      onCancel={closeModal}
      centered
      confirmLoading={isDeleting}
      okText="Удалить"
      okButtonProps={{ danger: true }}
      cancelText="Отмена"
    >
      <p>Удалить тикер <strong>{ticker.name}</strong> ({ticker.symbol})?</p>
      <p style={{ color: '#ff4d4f', fontSize: 13 }}>Тикер будет удалён только если не используется в портфелях, кошельках и транзакциях.</p>
    </Modal>
  );
};
