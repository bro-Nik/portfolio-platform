import React from 'react';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { useAssetData } from 'src/modules/portfolios/hooks/useAssetData';
import AssetHeader from './AssetHeader';
import AssetStatistic from './AssetStatistic';
import AssetDetails from './AssetDetails';
import AssetTable from './AssetTable';

const PortfolioAssetPage = ({ portfolio, asset }) => {
  const { assetData, loading } = useAssetData(portfolio, asset);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="asset-detail">
      <AssetHeader portfolio={portfolio} asset={assetData} />
      <AssetStatistic portfolio={portfolio} asset={assetData} />
      <AssetDetails data={assetData} />
      <AssetTable portfolio={portfolio} asset={assetData} transactions={assetData.transactions} />
    </div>
  );
};

export default PortfolioAssetPage;
