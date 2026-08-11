import React from 'react';
import { formatCurrencyFromUsd, formatPercentage, formatProfit, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';
import { useDisplayCurrency } from 'src/utils/currency';

const PortfolioStatistic = ({ stats }) => {
  useDisplayCurrency();

  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrencyFromUsd(stats.costNow),
    },
    {
      title: 'Вложено',
      value: formatCurrencyFromUsd(stats.invested),
    },
    {
      title: 'Прибыль',
      value: formatProfit(stats.profit || 0, stats.invested || 0, stats.totalInvested),
      class: getColorClass(stats.profit),
    },
    {
      title: 'Доля',
      value: formatPercentage(stats.share || 0),
    },
  ];

  return <StatisticCards cards={statCards} />;
};

export default PortfolioStatistic;
