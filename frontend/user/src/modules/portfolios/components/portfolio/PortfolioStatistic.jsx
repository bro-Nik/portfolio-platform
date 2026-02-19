import React from 'react';
import { formatCurrency, formatPercentage, formatProfit, getColorClass } from '/app/src/utils/format';
import StatisticCards from '/app/src/features/statistics/StatisticCards';

const PortfolioStatistic = ({ stats }) => {

  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(stats.costNow),
      description: 'Общая стоимость активов по текущим ценам'
    },
    {
      title: 'Вложено',
      value: formatCurrency(stats.invested),
      description: 'Общая сумма инвестиций'
    },
    {
      title: 'Прибыль',
      value: formatProfit(stats.profit || 0, stats.invested || 0),
      class: getColorClass(stats.profit),
      description: 'Прибыль/убыток за все время'
    },
    {
      title: 'Доля',
      value: formatPercentage(stats.share || 0),
    },
  ];

  return <StatisticCards cards={statCards} />;
};

export default PortfolioStatistic;
