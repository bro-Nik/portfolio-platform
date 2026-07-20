import React from 'react';
import { formatCurrency, formatPercentage } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const WalletStatistic = ({ wallet }) => {
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(wallet.costNow),
    },
    {
      title: 'Доля',
      value: formatPercentage(wallet.share),
    },
    {
      title: 'В ордерах',
      value: formatCurrency(wallet.buyOrders),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default WalletStatistic;
