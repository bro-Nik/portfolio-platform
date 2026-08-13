import React from 'react';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { useModalStore } from '@portfolio/shared';
import { useAssetData } from 'src/modules/portfolios/hooks/useAssetData';
import EmptyState from 'src/components/EmptyState';
import AssetHeader from './AssetHeader';
import AssetStatistic from './AssetStatistic';
import AssetDetails from 'src/features/assets/AssetDetails';
import AssetTable from './AssetTable';
import TransactionEditModal from 'src/modules/transaction/modals/TransactionEdit';
import { ArrowLeftRight } from 'lucide-react';

const PortfolioAssetPage = ({ portfolio, asset, active }) => {
  const { assetData, loading } = useAssetData(portfolio, asset, { enabled: active });
  const { openModal } = useModalStore();

  if (loading) return <LoadingSpinner />;

  if (!assetData.transactions?.length) {
    return (
      <div className="asset-detail">
        <AssetHeader portfolio={portfolio} asset={assetData} />
        <EmptyState
          icon={ArrowLeftRight}
          title="В активе пока нет транзакций"
          description="Добавьте первую транзакцию, чтобы начать отслеживать движение средств"
          action={!assetData.isArchived ? { text: 'Добавить транзакцию', onClick: () => openModal(TransactionEditModal, { tickerId: assetData.tickerId, portfolioId: portfolio.id }) } : undefined}
        />
      </div>
    );
  }

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
