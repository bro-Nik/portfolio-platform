import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { useAssetData } from 'src/modules/wallets/hooks/useAssetData';
import EmptyState from 'src/components/EmptyState';
import AssetHeader from './AssetHeader';
import AssetStatistic from './AssetStatistic';
import AssetTable from './AssetTable';
import { ArrowLeftRight } from 'lucide-react';

const WalletAssetPage = ({ wallet, asset, active }) => {
  const { assetData, loading } = useAssetData(wallet, asset, { enabled: active });

  if (loading) return <LoadingSpinner />;

  if (!assetData.transactions?.length) {
    return (
      <div className="asset-detail">
        <AssetHeader wallet={wallet} asset={assetData} />
        <EmptyState
          icon={ArrowLeftRight}
          title="В активе пока нет транзакций"
          description="Здесь будут отображаться транзакции актива"
        />
      </div>
    );
  }

  return (
    <div className="asset-detail">
      <AssetHeader wallet={wallet} asset={assetData} />
      <AssetStatistic wallet={wallet} asset={assetData} />
      <AssetTable wallet={wallet} asset={assetData} transactions={assetData.transactions} />
    </div>
  );
};

export default WalletAssetPage;
