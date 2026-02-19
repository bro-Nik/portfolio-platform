import React from 'react';
import LoadingSpinner from '/app/src/components/ui/LoadingSpinner';
import { useAssetData } from '/app/src/modules/wallets/hooks/useAssetData';
import AssetHeader from './AssetHeader';
import AssetStatistic from './AssetStatistic';
// import AssetDetails from './AssetDetails';
import AssetTable from './AssetTable';

const WalletAssetPage = ({ wallet, asset }) => {
  const { assetData, loading } = useAssetData(wallet, asset);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="asset-detail">
      <AssetHeader wallet={wallet} asset={assetData} />
      <AssetStatistic wallet={wallet} asset={assetData} />
      {/* <AssetDetails data={assetData} /> */}
      <AssetTable wallet={wallet} asset={assetData} transactions={assetData.transactions} />
    </div>
  );
};

export default WalletAssetPage;
