import React from 'react';
import { formatCurrency, formatPercentage } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

export const WalletsStatistic = ({ stats }) => {
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(stats.totalCostNow || 0),
    },
    {
      title: 'В ордерах',
      value: formatCurrency(stats.totalBuyOrders || 0),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default WalletsStatistic;
