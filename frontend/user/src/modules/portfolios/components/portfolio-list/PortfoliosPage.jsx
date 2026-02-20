import React from 'react';
import LoadingSpinner from '/app/src/components/ui/LoadingSpinner';
import { usePortfoliosData } from '/app/src/modules/portfolios/hooks/usePortfoliosData';
import PortfoliosHeader from './PortfoliosHeader';
import PortfoliosStatistic from './PortfoliosStatistic';
import PortfoliosTable from './PortfoliosTable';

const PortfoliosPage = () => {
  const { portfolios, overallStats, loading } = usePortfoliosData();

  if (loading) return <LoadingSpinner />;

  return (
    <>
      <PortfoliosHeader />

      <div className="row xs-mb-3">
        <PortfoliosStatistic stats={overallStats} />
      </div>

      <div className="row">
        <PortfoliosTable portfolios={portfolios} />
      </div>
    </>
  );
};

export default PortfoliosPage;
