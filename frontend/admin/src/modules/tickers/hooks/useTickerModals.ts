import { useModalStore } from '@portfolio/shared';
import { TickerEditModal } from '../components/TickerEditModal';
import { TickerMergeModal } from '../components/TickerMergeModal';
import { TickerDelModal } from '../components/TickerDelModal';
import { Ticker } from '../../../types/ticker';

export const useTickerModals = () => {
  const { openModal } = useModalStore();

  return {
    editModal: (ticker: Ticker) => openModal(TickerEditModal, { ticker }),
    mergeModal: () => openModal(TickerMergeModal, {}),
    deleteConfirmModal: (ticker: Ticker) => openModal(TickerDelModal, { ticker }),
  };
};
