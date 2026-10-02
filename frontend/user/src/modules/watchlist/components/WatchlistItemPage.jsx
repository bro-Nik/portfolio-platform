import React from 'react';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { useModalStore } from '@portfolio/shared';
import EmptyState from 'src/components/EmptyState';
import WatchlistItemHeader from './WatchlistItemHeader';
import WatchlistItemStatistic from './WatchlistItemStatistic';
import WatchlistAlertsTable from './WatchlistAlertsTable';
import AlertEditModal from './modals/AlertEdit';
import { BellRing } from 'lucide-react';

const WatchlistItemPage = ({ item }) => {
  const { openModal } = useModalStore();

  if (!item) return <LoadingSpinner />;

  if (!item.alerts?.length) {
    return (
      <div className="asset-detail">
        <WatchlistItemHeader item={item} />
        <EmptyState
          icon={BellRing}
          title="Уведомлений пока нет"
          description="Добавьте первое ценовое уведомление, чтобы следить за активом"
          action={!item.isArchived
            ? { text: 'Добавить уведомление', onClick: () => openModal(AlertEditModal, { item }) }
            : undefined}
        />
      </div>
    );
  }

  return (
    <div className="asset-detail">
      <WatchlistItemHeader item={item} />
      <WatchlistItemStatistic item={item} />
      <WatchlistAlertsTable item={item} />
    </div>
  );
};

export default WatchlistItemPage;
