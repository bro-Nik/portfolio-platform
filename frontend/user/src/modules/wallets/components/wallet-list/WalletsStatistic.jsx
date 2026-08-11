import React from 'react';
import { formatCurrencyFromUsd } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { useDisplayCurrency } from 'src/utils/currency';

export const WalletsStatistic = ({ stats }) => {
  useDisplayCurrency();
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(stats.totalCostNow || 0),
    },
    {
      title: 'В ордерах',
      value: formatCurrencyFromUsd(stats.totalBuyOrders || 0),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default WalletsStatistic;
