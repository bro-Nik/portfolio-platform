import React from 'react';
import { formatCurrency, formatPercentage, formatProfit, getColorClass } from 'src/utils/format';
import StatisticCards from 'src/features/statistics/StatisticCards';

const PortfolioStatistic = ({ stats }) => {

  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(stats.costNow),
    },
    {
      title: 'Вложено',
      value: formatCurrency(stats.invested),
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
