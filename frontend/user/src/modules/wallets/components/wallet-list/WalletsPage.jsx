import React from 'react';
import { useModalStore } from '@portfolio/shared';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import EmptyState from 'src/components/EmptyState';
import WalletEditModal from 'src/modules/wallets/components/modals/WalletEdit';
import WalletsHeader from './WalletsHeader';
import WalletsStatistic from './WalletsStatistic';
import WalletsTable from './WalletsTable';
import { Wallet } from 'lucide-react';

const WalletsPage = () => {
  const { wallets, overallStats, loading } = useWalletsData();
  const { openModal } = useModalStore();

  if (loading) return <LoadingSpinner />;

  if (!wallets.length) {
    return (
      <>
        <WalletsHeader />
        <EmptyState
          icon={Wallet}
          title="У вас пока нет кошельков"
          description="Добавьте кошелёк, чтобы отслеживать остатки средств"
          action={{ text: 'Создать кошелёк', onClick: () => openModal(WalletEditModal) }}
        />
      </>
    );
  }

  return (
    <>
      <WalletsHeader />
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <WalletsStatistic stats={overallStats} />
      </div>
      <WalletsTable wallets={wallets} />
    </>
  );
};

export default WalletsPage;
