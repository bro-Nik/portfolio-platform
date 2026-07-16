import React from 'react';
import LoadingSpinner from 'src/components/ui/LoadingSpinner';
import { usePortfoliosData } from 'src/modules/portfolios/hooks/usePortfoliosData';
import PortfoliosHeader from './PortfoliosHeader';
import PortfoliosStatistic from './PortfoliosStatistic';
import PortfoliosTable from './PortfoliosTable';

const PortfoliosPage = () => {
  const { portfolios, overallStats, loading } = usePortfoliosData();

  if (loading) return <LoadingSpinner />;

  return (
    <>
      <PortfoliosHeader />

      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        <PortfoliosStatistic stats={overallStats} />
      </div>

      <PortfoliosTable portfolios={portfolios} />
    </>
  );
};

export default PortfoliosPage;
