import React from 'react';
import { useWalletsData } from 'src/modules/wallets/hooks/useWalletsData';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import WalletsHeader from './WalletsHeader';
import WalletsStatistic from './WalletsStatistic';
import WalletsTable from './WalletsTable';

const WalletsPage = () => {
  const { wallets, overallStats, loading } = useWalletsData();

  if (loading) return <LoadingSpinner />;

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
