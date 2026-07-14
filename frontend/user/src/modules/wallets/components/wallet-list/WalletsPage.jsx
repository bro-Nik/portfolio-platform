import React from 'react';
import { useWalletsData } from '/app/src/modules/wallets/hooks/useWalletsData';
import LoadingSpinner from '/app/src/components/ui/LoadingSpinner';
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

      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <WalletsTable wallets={wallets} />
      </div>
    </>
  );
};

export default WalletsPage;
