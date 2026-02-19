import PortfolioTable from './PortfolioTable';
import PortfolioStatistic from './PortfolioStatistic';
import PortfolioHeader from './PortfolioHeader';

const PortfolioPage = ({ portfolio }) => {

  return (
    <>
      <PortfolioHeader portfolio={portfolio} />
      <PortfolioStatistic stats={portfolio} />
      <PortfolioTable portfolio={portfolio} assets={portfolio.assets} />
    </>
  );
};

export default PortfolioPage;
