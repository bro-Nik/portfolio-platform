import PortfolioTable from './PortfolioTable';
import PortfolioStatistic from './PortfolioStatistic';
import PortfolioHeader from './PortfolioHeader';

const PortfolioPage = ({ portfolio, onRefresh }) => {

  return (
    <>
      <PortfolioHeader portfolio={portfolio} onRefresh={onRefresh} />
      <PortfolioStatistic stats={portfolio} />
      <PortfolioTable portfolio={portfolio} assets={portfolio.assets} onRefresh={onRefresh} />
    </>
  );
};

export default PortfolioPage;
