import React from 'react';
import { formatCurrency, formatPercentage, formatProfit, getColorClass } from '/app/src/utils/format';
import StatisticCards from '/app/src/features/statistics/StatisticCards';

const PortfoliosStatistic = ({ stats }) => {
  const statCards = [
    {
      title: 'Стоимость',
      value: formatCurrency(stats.totalCostNow || 0),
    },
    {
      title: 'Вложено',
      value: formatCurrency(stats.totalInvested || 0),
    },
    {
      title: 'Прибыль',
      value: formatProfit(stats.totalProfit || 0, stats.totalInvested || 0),
      class: getColorClass(stats.totalProfit),
    },
    {
      title: 'В ордерах',
      value: formatCurrency(stats.totalBuyOrders || 0),
    }
  ];

  return <StatisticCards cards={statCards} />;
};

export default PortfoliosStatistic;
