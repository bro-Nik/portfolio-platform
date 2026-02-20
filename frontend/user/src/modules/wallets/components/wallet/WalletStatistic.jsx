import React from 'react';
import { formatCurrency, formatPercentage } from '/app/src/utils/format';
import StatisticCards from '/app/src/features/statistics/StatisticCards';

const WalletStatistic = ({ wallet }) => {
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(wallet.costNow),
      description: 'Общая стоимость активов по текущим ценам'
    },
    {
      title: 'Доля',
      value: formatPercentage(wallet.share),
      description: 'Доля от всех кошельков'
    },
    {
      title: 'В ордерах',
      value: formatCurrency(wallet.buyOrders),
      description: 'В ордерах на покупку'
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default WalletStatistic;
