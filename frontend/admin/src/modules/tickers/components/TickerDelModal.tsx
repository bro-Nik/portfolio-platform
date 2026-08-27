import { ConfirmDeleteModal, useModalStore } from '@portfolio/shared';
import { useTickerActions } from '../hooks/useTickerActions';
import { Ticker } from '../../../types/ticker';

interface TickerDelModalProps { ticker: Ticker }

export const TickerDelModal: React.FC<TickerDelModalProps> = ({ ticker }) => {
  const { closeModal } = useModalStore();
  const { deleteTicker } = useTickerActions();

  return (
    <ConfirmDeleteModal
      title="Удаление тикера"
      question={<>Удалить тикер <strong>{ticker.name}</strong> ({ticker.symbol})?</>}
      extraNote={
        <p style={{ color: '#ff4d4f', fontSize: 13 }}>
          Тикер будет удалён только если не используется в портфелях, кошельках и транзакциях.
        </p>
      }
      onConfirm={() => {
        deleteTicker(ticker.id);
      }}
      onCancel={closeModal}
    />
  );
};
