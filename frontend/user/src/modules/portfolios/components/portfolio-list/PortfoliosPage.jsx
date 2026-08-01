import React from 'react';
import { usePersistedState } from '@portfolio/shared';
import { useModalStore } from '@portfolio/shared';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import EmptyState from 'src/components/EmptyState';
import PortfolioEditModal from 'src/modules/portfolios/components/modals/PortfolioEdit';
import PortfoliosHeader from './PortfoliosHeader';
import PortfoliosStatistic from './PortfoliosStatistic';
import PortfoliosTable from './PortfoliosTable';
import { Briefcase } from 'lucide-react';

const PortfoliosPage = () => {
  const [showArchived, setShowArchived] = usePersistedState('portfolios-show-archived', false);
  const { portfolios, allPortfolios, overallStats, loading, showingArchivedFallback } = usePortfoliosData(showArchived);
  const { openModal } = useModalStore();

  if (loading) return <LoadingSpinner />;

  if (!allPortfolios.length) {
    return (
      <>
        <PortfoliosHeader />
        <EmptyState
          icon={Briefcase}
          title="У вас пока нет портфелей"
          description="Создайте портфель и начните отслеживать свои инвестиции"
          action={{ text: 'Создать портфель', onClick: () => openModal(PortfolioEditModal) }}
        />
      </>
    );
  }

  return (
    <>
      <PortfoliosHeader />
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <PortfoliosStatistic stats={overallStats} />
      </div>
      <PortfoliosTable portfolios={portfolios} showArchived={showArchived} onToggleArchived={setShowArchived} showingArchivedFallback={showingArchivedFallback} />
    </>
  );
};

export default PortfoliosPage;
