import React from 'react';
import { usePersistedState } from '@portfolio/shared';
import { useModalStore } from '@portfolio/shared';
import { useWatchlistData } from '../hooks/useWatchlistData';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import EmptyState from 'src/components/EmptyState';
import WatchlistAssetAddModal from './modals/WishlistAssetAdd';
import WatchlistHeader from './WatchlistHeader';
import WatchlistStatistic from './WatchlistStatistic';
import WatchlistTable from './WishlistTable';
import { Star } from 'lucide-react';

const WatchlistPage = () => {
  const [showArchived, setShowArchived] = usePersistedState('watchlist-show-archived', false);
  const { items, allItems, stats, loading, showingArchivedFallback } = useWatchlistData(showArchived);
  const { openModal } = useModalStore();

  if (loading) return <LoadingSpinner />;

  if (!allItems.length) {
    return (
      <>
        <WatchlistHeader />
        <EmptyState
          icon={Star}
          title="Вы пока ничего не отслеживаете"
          description="Добавьте актив в избранное и создайте ценовое уведомление"
          action={{ text: 'Добавить актив', onClick: () => openModal(WatchlistAssetAddModal) }}
        />
      </>
    );
  }

  return (
    <>
      <WatchlistHeader />
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <WatchlistStatistic stats={stats} />
      </div>
      <WatchlistTable
        items={items}
        showArchived={showArchived}
        onToggleArchived={setShowArchived}
        showingArchivedFallback={showingArchivedFallback}
      />
    </>
  );
};

export default WatchlistPage;
