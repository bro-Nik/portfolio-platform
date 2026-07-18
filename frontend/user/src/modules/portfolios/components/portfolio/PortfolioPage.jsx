import { useModalStore } from '@portfolio/shared';
import EmptyState from 'src/components/EmptyState';
import AssetAddModal from 'src/modules/portfolios/components/modals/AssetAdd';
import PortfolioTable from './PortfolioTable';
import PortfolioStatistic from './PortfolioStatistic';
import PortfolioHeader from './PortfolioHeader';
import { Coins } from 'lucide-react';

const PortfolioPage = ({ portfolio, onRefresh }) => {
  const { openModal } = useModalStore();

  if (!portfolio.assets?.length) {
    return (
      <>
        <PortfolioHeader portfolio={portfolio} onRefresh={onRefresh} />
        <EmptyState
          icon={Coins}
          title="В портфеле пока нет активов"
          description="Добавьте первый актив, чтобы начать отслеживать инвестиции"
          action={{ text: 'Добавить актив', onClick: () => openModal(AssetAddModal, { portfolio }) }}
        />
      </>
    );
  }

  return (
    <>
      <PortfolioHeader portfolio={portfolio} onRefresh={onRefresh} />
      <PortfolioStatistic stats={portfolio} />
      <PortfolioTable portfolio={portfolio} assets={portfolio.assets} onRefresh={onRefresh} />
    </>
  );
};

export default PortfolioPage;
